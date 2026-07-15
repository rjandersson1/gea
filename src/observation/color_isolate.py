"""
src/observation/color_isolate.py

Responsibilities:
  - Isolate HUD-green pixels from a BGR image via inRange threshold
  - Shared by ROI detection and OCR preprocessing

Dependencies:
  - numpy
  - opencv-python
"""

import numpy as np
import cv2


class ColorIsolator:

    def __init__(self, target_bgr: tuple = (0, 251, 0), margin: int = 100):
        self.target_bgr = target_bgr
        self.margin = margin

    def isolate(self, img_bgr: np.ndarray) -> np.ndarray:
        lower = np.array([max(c - self.margin, 0) for c in self.target_bgr])
        upper = np.array([min(c + self.margin, 255) for c in self.target_bgr])
        return cv2.inRange(img_bgr, lower, upper)