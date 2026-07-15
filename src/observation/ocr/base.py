"""
src/observation/ocr/base.py

Responsibilities:
  - Shared OCR extraction for tape-style ROIs (heading, airspeed, altitude)
  - Preprocess crop via HUD-green color isolation
  - Extract all tesseract tokens with bounding boxes
  - Select the token nearest the ROI's centre axis (orientation-dependent)
  - Convert token to float, reject on outlier_threshold

Subclass contract:
  - whitelist:          str, tesseract char whitelist
  - outlier_threshold:  float, reject abs(value) above this
  - orientation:         'vertical' (values stacked top-to-bottom) or
                          'horizontal' (values spaced left-to-right)
  - override _token_to_value() for non-numeric tokens (e.g. cardinals)

Dependencies:
  - numpy
  - opencv-python
  - pytesseract
  - src/observation/color_isolate.py
"""

import re
import numpy as np
import pytesseract

from src.observation.color_isolate import ColorIsolator


class BaseOCR:

    whitelist = '0123456789'
    outlier_threshold = float('inf')
    orientation = 'vertical'
    psm = 11

    def __init__(self, isolator: ColorIsolator = None):
        self.isolator = isolator or ColorIsolator()

    def parse(self, img: np.ndarray) -> float | None:
        token = self._extract_centre_token(img)
        if token is None:
            return None
        value = self._token_to_value(token)
        if value is None:
            return None
        if abs(value) > self.outlier_threshold:
            return None
        return value

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        return self.isolator.isolate(img)

    def _extract_centre_token(self, img: np.ndarray) -> str | None:
        mask = self._preprocess(img)
        config = f"--psm {self.psm} -c tessedit_char_whitelist={self.whitelist}"
        data = pytesseract.image_to_data(mask, config=config, output_type=pytesseract.Output.DICT)

        h, w = mask.shape[:2]
        mid = h / 2 if self.orientation == 'vertical' else w / 2

        best_token, best_dist = None, float('inf')
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if not text:
                continue
            try:
                conf = int(float(data['conf'][i]))
            except (ValueError, TypeError):
                conf = -1
            if conf < 0:
                continue

            x, y, tw, th = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            center = (y + th / 2) if self.orientation == 'vertical' else (x + tw / 2)
            dist = abs(center - mid)
            if dist < best_dist:
                best_dist = dist
                best_token = text

        return best_token

    def _token_to_value(self, token: str) -> float | None:
        cleaned = re.sub(r'[^0-9.\-]', '', token)
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None