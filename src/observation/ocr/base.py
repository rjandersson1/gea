"""
observation/ocr/base.py

Responsibilities:
  - Shared preprocessing pipeline for all OCR fields:
      upscale → threshold → denoise → tesseract call
  - Subclasses override tesseract_config and parse() only
  - Returns None on any parse failure (empty string, exception,
    non-numeric output) — never raises, never returns garbage
  - outlier_threshold checked here; values exceeding it return None

Dependencies:
  - numpy
  - opencv-python    (cv2)     for preprocessing
  - pytesseract                for OCR
  - src/utils/config.py        (loads ocr.yaml)
  - src/observation/color_isolate.py
"""

import numpy as np
import cv2
import pytesseract

from src.utils.config import load_config
from src.observation.color_isolate import ColorIsolator


class BaseOCR:

    # override in subclasses
    tesseract_config: str = '--psm 7'
    whitelist: str = '0123456789'
    outlier_threshold: float = float('inf')

    def __init__(self, isolator: ColorIsolator, ocr_config: dict):
        """
        Args:
            isolator:   ColorIsolator instance (shared across parsers)
            ocr_config: preprocessing section from ocr.yaml
        """
        pass

    def preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        Apply color isolation, upscale, threshold, denoise.

        Returns:
            Grayscale preprocessed image ready for tesseract
        """
        pass

    def parse(self, img: np.ndarray) -> float | None:
        """
        Run full pipeline: preprocess → tesseract → validate.

        Returns:
            Parsed float value, or None on any failure
        """
        pass

    def _run_tesseract(self, img: np.ndarray) -> str:
        """Raw tesseract call. Returns string output."""
        pass

    def _validate(self, value: float) -> float | None:
        """Return None if value exceeds outlier_threshold."""
        pass
