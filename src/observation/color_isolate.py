"""
observation/color_isolate.py

Responsibilities:
  - Isolate HUD green (#00FC00) from background using RGB cube mask
  - Apply morphological dilation to recover anti-aliased stroke edges
  - Return masked image (non-matching pixels set to black)
  - Also expose binary mask for downstream CV operations

Dependencies:
  - numpy
  - scipy.ndimage    (binary_dilation)
  - src/utils/config.py    (loads ocr.yaml for defaults)
"""

import numpy as np
from scipy.ndimage import binary_dilation

from src.utils.config import load_config


class ColorIsolator:

    def __init__(self, target_rgb: list, margin: int, dilation_radius: int):
        """
        Args:
            target_rgb:       [R, G, B] target color e.g. [0, 252, 0]
            margin:           per-channel tolerance (RGB cube half-width)
            dilation_radius:  structuring element radius in pixels
        """
        pass

    @classmethod
    def from_config(cls, config_path: str) -> 'ColorIsolator':
        """Construct from ocr.yaml color_isolator section."""
        pass

    def get_mask(self, img: np.ndarray) -> np.ndarray:
        """
        Compute binary mask of pixels within margin of target_rgb,
        then dilate by dilation_radius.

        Returns:
            Boolean HxW numpy array
        """
        pass

    def isolate(self, img: np.ndarray) -> np.ndarray:
        """
        Apply mask to image. Non-masked pixels set to black.

        Returns:
            HxWx3 numpy array, non-green pixels zeroed
        """
        pass
