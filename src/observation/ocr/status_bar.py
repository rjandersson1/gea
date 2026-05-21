"""
observation/ocr/status_bar.py

Responsibilities:
  - Parse eye_alt from the bottom status bar (white text on dark bar)
  - No color isolation needed — bar has sufficient contrast natively
  - Use regex to extract labelled fields robustly
    e.g. 'eye alt  258 m' → 258.0
  - eye_alt is the only reliable aircraft-linked value in the status bar
  - lat/lon/elev from status bar are cursor position — DO NOT USE

Dependencies:
  - numpy
  - cv2
  - pytesseract
  - re
"""

import re
import numpy as np
import cv2
import pytesseract


class StatusBarParser:

    def parse(self, img: np.ndarray) -> dict:
        """
        Parse eye_alt from status bar image.

        Returns:
            dict with key 'eye_alt': float|None
            e.g. {'eye_alt': 258.0}
        """
        pass

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        """Grayscale + threshold for white text on dark background."""
        pass

    def _extract_eye_alt(self, text: str) -> float | None:
        """Regex match 'eye alt <value> m' from tesseract output."""
        pass
