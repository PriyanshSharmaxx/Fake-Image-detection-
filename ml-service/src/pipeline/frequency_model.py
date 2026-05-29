import cv2
import numpy as np
import torch
import timm
from torchvision import transforms
from PIL import Image


class FrequencyModelDetector:
    def __init__(self, pretrained: bool = True) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # We classify 2D power spectrums using a ResNet-50 backend (binary mapping)
        try:
            self.model = timm.create_model("resnet50", pretrained=pretrained, num_classes=2)
        except Exception:
            self.model = timm.create_model("resnet50", pretrained=False, num_classes=2)
            
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def compute_dct_log_spectrum(self, img_patch: np.ndarray) -> np.ndarray:
        """
        Compute the 2D Discrete Cosine Transform (DCT) log-magnitude spectrum.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img_patch, cv2.COLOR_BGR2GRAY) if img_patch.ndim == 3 else img_patch
        
        # Compute DCT
        dct = cv2.dct(np.float32(gray) / 255.0)
        
        # Take log magnitude to capture structural artifacts clearly
        dct_log = np.log(np.abs(dct) + 1e-6)
        
        # Normalize to uint8 image range [0, 255]
        dct_norm = cv2.normalize(dct_log, None, 0, 255, cv2.NORM_MINMAX)
        dct_uint8 = np.uint8(dct_norm)
        
        # Replicate grayscale to 3-channels to match standard ResNet input layers
        dct_3ch = cv2.merge([dct_uint8, dct_uint8, dct_uint8])
        return dct_3ch

    def predict(self, face_patch: np.ndarray) -> np.ndarray:
        """
        Extract frequency spectrum and predict probabilities.
        """
        spectrum = self.compute_dct_log_spectrum(face_patch)
        pil_img = Image.fromarray(spectrum)
        
        tensor_img = self.transform(pil_img).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(tensor_img)
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
            
        return probabilities
