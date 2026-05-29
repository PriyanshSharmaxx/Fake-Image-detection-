import os
import torch
import torch.nn as nn
from typing import Optional
from torchvision import transforms
import timm
import numpy as np
from PIL import Image
import cv2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spatial-model")


class SpatialModelDetector:
    def __init__(self, model_name: str = "efficientnet_b0", weights_path: Optional[str] = None) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = model_name
        
        # Implement model selection priority: TorchScript > Optimized > Standard
        resolved_path = self._resolve_model_path(weights_path)

        logger.info(f"Using execution device: {self.device}")
        logger.info(f"Initializing model architecture: {self.model_name}")
        logger.info(f"Loading model weights from: {resolved_path}")
        
        # Instantiate base EfficientNet-B0 with 2 target classes (0=ai_generated, 1=real)
        self.model = timm.create_model(self.model_name, pretrained=False, num_classes=2)
        
        if os.path.exists(resolved_path):
            logger.info(f"Loading trained weights from: {resolved_path}")
            try:
                state_dict = torch.load(resolved_path, map_location=self.device)
                
                # Check if it's a full model checkpoint rather than just state_dict
                if "state_dict" in state_dict:
                    state_dict = state_dict["state_dict"]
                
                # Handle Google Colab DataParallel prefixes ('module.')
                cleaned_state_dict = {}
                for k, v in state_dict.items():
                    name = k.replace("module.", "") if k.startswith("module.") else k
                    cleaned_state_dict[name] = v
                
                # Load weights with safety verification checks
                missing_keys, unexpected_keys = self.model.load_state_dict(cleaned_state_dict, strict=False)
                
                if missing_keys:
                    logger.warning(f"Missing keys during state_dict loading: {missing_keys}")
                if unexpected_keys:
                    logger.warning(f"Unexpected keys during state_dict loading: {unexpected_keys}")
                    
                logger.info("Successfully loaded state dict weights.")
            except Exception as e:
                logger.error(f"Failed loading weights file: {str(e)}. Running with initialized random parameters.")
        else:
            logger.error(f"Weights file not found at {resolved_path}. Initializing with random parameters.")

        self.model.to(self.device)
        self.model.eval()

        # Input normalizations matching standard EfficientNet configuration
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        # Run pipeline warm-up sequence to prevent first-request cold-start latency
        self._warmup()

    def _resolve_model_path(self, weights_path: Optional[str] = None) -> str:
        """
        Resolve model path with priority order: TorchScript > Optimized > Standard.
        Searches in multiple locations to handle Docker, local, and cloud execution contexts.
        """
        # Priority order of model files to search for
        model_priorities = [
            "deepfake_model_scripted.pt",      # Priority 1: TorchScript compiled
            "deepfake_model_optimized.pth",    # Priority 2: Optimized model
            "deepfake_model.pth",               # Priority 3: Standard model
        ]
        
        # If explicit path provided, try that first
        if weights_path and os.path.exists(weights_path):
            return weights_path
        
        # Search locations in order of likelihood
        search_locations = [
            os.getcwd(),  # Current working directory
            "/workspace",  # Docker workspace
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # ml-service root
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models"),
        ]
        
        # Also check environment variable for custom path
        env_model_path = os.getenv("MODEL_PATH")
        if env_model_path:
            search_locations.insert(0, env_model_path)
        
        # Try each priority model in each location
        for location in search_locations:
            for model_file in model_priorities:
                candidate_path = os.path.join(location, model_file)
                if os.path.exists(candidate_path):
                    logger.info(f"Found model with priority '{model_file}' at {candidate_path}")
                    return candidate_path
        
        # Fallback: return the first priority model name (will log error later if not found)
        fallback_path = os.path.join(os.getcwd(), model_priorities[0])
        logger.warning(f"Could not find any model files. Using fallback path: {fallback_path}")
        return fallback_path

    def _warmup(self) -> None:
        logger.info("Starting pipeline warm-up inference sequence...")
        try:
            # Generate dummy image tensor matching target input size (3ch, 224x224)
            dummy_input = torch.zeros((1, 3, 224, 224), dtype=torch.float32).to(self.device)
            with torch.no_grad():
                _ = self.model(dummy_input)
            logger.info("Warm-up sequence completed successfully.")
        except Exception as e:
            logger.error(f"Error during warm-up execution: {str(e)}")

    def predict(self, face_patch: np.ndarray) -> np.ndarray:
        """
        Predict probability distribution of the face patch.
        Returns array of probabilities: [prob_fake (ai_generated), prob_real]
        """
        # Convert BGR (OpenCV default) to RGB
        rgb_patch = cv2.cvtColor(face_patch, cv2.COLOR_BGR2RGB) if face_patch.ndim == 3 else face_patch
        pil_img = Image.fromarray(rgb_patch)
        
        tensor_img = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor_img)
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
            
        return probabilities
