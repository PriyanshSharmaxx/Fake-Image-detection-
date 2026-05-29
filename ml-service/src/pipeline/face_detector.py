import cv2
import numpy as np
from typing import Tuple, List, Optional, Dict, Any


class FaceDetector:
    def __init__(self) -> None:
        # Load OpenCV Haar cascade for rapid fallback detection
        self.cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)

    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect bounding boxes of faces inside the image.
        Returns list of (x, y, w, h).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        return [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]

    def crop_and_align(self, image: np.ndarray, bbox: Tuple[int, int, int, int], target_size: int = 224) -> np.ndarray:
        """
        Crop face region with a padding margin and resize to target model resolution.
        """
        h_img, w_img, _ = image.shape
        x, y, w, h = bbox
        
        # Add padding factor (30% padding around face)
        pad_x = int(w * 0.15)
        pad_y = int(h * 0.15)
        
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w_img, x + w + pad_x)
        y2 = min(h_img, y + h + pad_y)
        
        face_crop = image[y1:y2, x1:x2]
        
        if face_crop.size == 0:
            return cv2.resize(image, (target_size, target_size))
            
        return cv2.resize(face_crop, (target_size, target_size))


face_detector = FaceDetector()
