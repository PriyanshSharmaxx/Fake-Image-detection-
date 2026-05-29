import time
import httpx
import cv2
import numpy as np
import torch
import torch.nn as nn
import io
import os
import uuid
import logging
from typing import Dict, Any, List, Tuple
from PIL import Image

from src.pipeline.face_detector import face_detector
from src.pipeline.spatial_model import SpatialModelDetector
from src.pipeline.frequency_model import FrequencyModelDetector
from src.explainability.gradcam import GradCAM, apply_colormap_on_image
from src.services.s3_helper import ml_s3_helper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ensemble-pipeline")


class EnsembleDetector:
    def __init__(self) -> None:
        # Load spatial and frequency detectors
        # Loaded once as a singleton within the running process
        self.spatial_detector = SpatialModelDetector()
        self.freq_detector = FrequencyModelDetector()
        
        # Configure Grad-CAM target layer dynamically
        self.target_layer = self._find_target_layer(self.spatial_detector.model)
        self.grad_cam = GradCAM(self.spatial_detector.model, self.target_layer)
        
        # Ensemble weight balance (65% Spatial texture, 35% Frequency periodicity)
        self.spatial_weight = 0.65
        self.freq_weight = 0.35
        
        # Binary class mapping matching model_config.json:
        # Index 0 -> FAKE (ai_generated), Index 1 -> REAL (real)
        self.classes = ["ai_generated", "real"]
        logger.info(f"Ensemble loaded with classes: {self.classes}")

    def _find_target_layer(self, model: nn.Module) -> nn.Module:
        """
        Dynamically find the last conv layer of the network for Grad-CAM.
        For EfficientNet-B0, it targets the model.conv_head module.
        """
        # Target head convolution for EfficientNet-B0
        if hasattr(model, "conv_head"):
            logger.info("Grad-CAM target resolved: model.conv_head")
            return model.conv_head
            
        # Target final stage blocks in ConvNeXt/other models
        if hasattr(model, "stages") and len(model.stages) > 0:
            last_stage = model.stages[-1]
            if hasattr(last_stage, "blocks") and len(last_stage.blocks) > 0:
                logger.info("Grad-CAM target resolved: model.stages[-1].blocks[-1]")
                return last_stage.blocks[-1]
                
        # Search backward for any Conv2d module
        for name, module in reversed(list(model.named_modules())):
            if isinstance(module, nn.Conv2d):
                logger.info(f"Grad-CAM target fallback resolved: {name}")
                return module
        raise ValueError("Could not dynamically resolve a suitable target layer for Grad-CAM.")

    async def _download_image(self, url: str) -> np.ndarray:
        """
        Fetch image bytes from signed URL and convert to OpenCV NumPy array.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=15.0)
            if response.status_code != 200:
                raise ValueError(f"Failed to download image from S3: HTTP {response.status_code}")
            
            image_bytes = response.content
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Downloaded data could not be parsed as an image.")
            return img

    async def analyze(self, image_s3_url: str, generate_heatmap: bool = True, threshold: float = 0.5) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Download image
        img = await self._download_image(image_s3_url)
        h_orig, w_orig, _ = img.shape

        # 2. Face Detection
        faces = face_detector.detect_faces(img)
        detections = []
        heatmap_s3_url = ""

        # Use full image if no faces are detected
        patches_to_process: List[Tuple[np.ndarray, Optional[Tuple[int, int, int, int]]]] = []
        if not faces:
            patches_to_process.append((cv2.resize(img, (224, 224)), None))
        else:
            for bbox in faces:
                crop = face_detector.crop_and_align(img, bbox, target_size=224)
                patches_to_process.append((crop, bbox))

        # 3. Predict spatial and frequency outputs per patch
        for i, (patch, bbox) in enumerate(patches_to_process):
            spatial_probs = self.spatial_detector.predict(patch)
            freq_probs = self.freq_detector.predict(patch)
            
            # Weighted fusion
            fused_probs = (self.spatial_weight * spatial_probs) + (self.freq_weight * freq_probs)
            pred_idx = int(np.argmax(fused_probs))
            classification = self.classes[pred_idx]
            confidence = float(fused_probs[pred_idx])

            # Compile bounding box representation
            bbox_meta = None
            if bbox:
                x, y, w, h = bbox
                bbox_meta = {
                    "xmin": float(x / w_orig),
                    "ymin": float(y / h_orig),
                    "xmax": float((x + w) / w_orig),
                    "ymax": float((y + h) / h_orig)
                }

            detections.append({
                "classification": classification,
                "confidence": confidence * 100.0,
                "spatial_score": float(spatial_probs[pred_idx]),
                "freq_score": float(freq_probs[pred_idx]),
                "bbox": bbox_meta,
                "patch": patch,
                "pred_idx": pred_idx
            })

        # 4. Generate Grad-CAM Heatmap for primary threat (highest confidence FAKE patch)
        if generate_heatmap and detections:
            # Find the most threatening patch (non-real, i.e., ai_generated)
            non_real_detections = [d for d in detections if d["classification"] != "real"]
            target_det = non_real_detections[0] if non_real_detections else detections[0]
            
            target_patch = target_det["patch"]
            pred_idx = target_det["pred_idx"]
            
            # Form tensor
            rgb_patch = cv2.cvtColor(target_patch, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_patch)
            input_tensor = self.spatial_detector.transform(pil_img).unsqueeze(0).to(self.spatial_detector.device)
            
            try:
                # Compute activations
                heatmap = self.grad_cam.generate_heatmap(input_tensor, class_idx=pred_idx)
                overlay = apply_colormap_on_image(target_patch, heatmap)
                
                # Save overlay image to bytes
                _, buffer = cv2.imencode(".jpg", overlay)
                heatmap_bytes = buffer.tobytes()
                
                # Upload heatmap to S3
                heatmap_key = f"heatmaps/{uuid.uuid4()}.jpg"
                await ml_s3_helper.upload_bytes(heatmap_bytes, heatmap_key, "image/jpeg")
                heatmap_s3_url = heatmap_key
            except Exception as e:
                logger.error(f"Grad-CAM generation failed: {str(e)}")

        latency_ms = int((time.time() - start_time) * 1000)

        # Clear patch raw images to prevent memory footprint leaks
        cleaned_detections = []
        for det in detections:
            cleaned_detections.append({
                "classification": det["classification"],
                "confidence": det["confidence"],
                "spatial_score": det["spatial_score"],
                "freq_score": det["freq_score"],
                "bbox": det["bbox"]
            })

        return {
            "detection_id": str(uuid.uuid4()),
            "detections": cleaned_detections,
            "heatmap_s3_url": heatmap_s3_url,
            "inference_time_ms": latency_ms
        }


ensemble_detector = EnsembleDetector()
