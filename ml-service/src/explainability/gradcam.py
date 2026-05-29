from typing import Any, Tuple, Optional
import logging

import torch
import torch.nn as nn
import cv2
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gradcam")


class GradCAM:
    """
    Gradient-weighted Class Activation Mapping for EfficientNet-B0 and similar architectures.
    Registers forward/backward hooks on the target convolutional layer to capture
    feature activations and their gradients during backpropagation.
    """

    def __init__(self, model: nn.Module, target_layer: nn.Module) -> None:
        self.model = model
        self.target_layer = target_layer
        self.gradients: Optional[torch.Tensor] = None
        self.activations: Optional[torch.Tensor] = None

        # Register forward hook to capture feature activations
        self._fwd_handle = self.target_layer.register_forward_hook(self._save_activation)
        # Register backward hook to capture gradient flow
        self._bwd_handle = self.target_layer.register_full_backward_hook(self._save_gradient)

        logger.info(f"GradCAM initialized on layer: {type(target_layer).__name__}")

    def _save_activation(self, module: nn.Module, input_args: Any, output: torch.Tensor) -> None:
        # Detach to avoid retaining the computation graph unnecessarily
        self.activations = output.detach()

    def _save_gradient(self, module: nn.Module, grad_input: Any, grad_output: Tuple[torch.Tensor, ...]) -> None:
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor: torch.Tensor, class_idx: Optional[int] = None) -> np.ndarray:
        """
        Generate a normalized float32 heatmap [0..1] from class-index gradients.
        The model is temporarily set to train mode so that gradients propagate
        through BatchNorm layers, then restored to eval mode.
        """
        # We need gradients, so temporarily enable train mode for BN layers
        was_training = self.model.training
        self.model.train()

        # Reset stored values
        self.gradients = None
        self.activations = None

        # Enable gradient tracking on input
        input_tensor = input_tensor.requires_grad_(True)

        self.model.zero_grad()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = int(torch.argmax(output, dim=1).item())

        # Create one-hot target vector
        one_hot = torch.zeros((1, output.size(-1)), dtype=torch.float32, device=input_tensor.device)
        one_hot[0][class_idx] = 1.0

        # Backpropagate
        output.backward(gradient=one_hot, retain_graph=True)

        # Restore original mode
        if not was_training:
            self.model.eval()

        if self.gradients is None or self.activations is None:
            logger.warning("GradCAM hooks did not fire. Returning blank heatmap.")
            return np.zeros((224, 224), dtype=np.float32)

        # Global average pooling of gradients across spatial dims
        gradients = self.gradients.cpu().numpy()[0]   # (C, H, W)
        activations = self.activations.cpu().numpy()[0]  # (C, H, W)
        weights = np.mean(gradients, axis=(1, 2))     # (C,)

        # Weighted combination of feature maps
        heatmap = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            heatmap += w * activations[i]

        # ReLU — keep only positive contributions
        heatmap = np.maximum(heatmap, 0)

        # Normalize to [0, 1]
        hmin, hmax = np.min(heatmap), np.max(heatmap)
        if hmax - hmin > 0:
            heatmap = (heatmap - hmin) / (hmax - hmin)
        else:
            heatmap = np.zeros_like(heatmap)

        return heatmap


def apply_colormap_on_image(
    org_img: np.ndarray,
    heatmap: np.ndarray,
    colormap: int = cv2.COLORMAP_JET,
    alpha: float = 0.5
) -> np.ndarray:
    """
    Overlay a Grad-CAM heatmap on the original image patch.
    """
    resized_heatmap = cv2.resize(heatmap, (org_img.shape[1], org_img.shape[0]))
    heatmap_color = cv2.applyColorMap(np.uint8(255 * resized_heatmap), colormap)

    overlay = cv2.addWeighted(org_img, alpha, heatmap_color, 1.0 - alpha, 0)
    return overlay
