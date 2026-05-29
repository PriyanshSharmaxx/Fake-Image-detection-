import pytest
import numpy as np
from src.pipeline.face_detector import face_detector
from src.pipeline.frequency_model import FrequencyModelDetector


def test_face_detector_crop():
    # Create empty black mock image
    mock_img = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Try cropping center patch with artificial bbox
    crop = face_detector.crop_and_align(mock_img, (50, 50, 100, 100), target_size=224)
    assert crop.shape == (224, 224, 3)


def test_dct_spectrum():
    detector = FrequencyModelDetector(pretrained=False)
    mock_patch = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    spectrum = detector.compute_dct_log_spectrum(mock_patch)
    assert spectrum.shape == (224, 224, 3)
    assert spectrum.dtype == np.uint8
