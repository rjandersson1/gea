"""
src/observation/ocr/base.py

Responsibilities:
  - Shared OCR extraction for tape-style ROIs (heading, airspeed, altitude)
  - Preprocess crop via HUD-green color isolation
  - Uses tesserocr (in-process Tesseract API binding) instead of pytesseract
    to avoid per-call subprocess spawn overhead
  - Keeps one PyTessBaseAPI instance alive per parser instance, reused
    across all parse() calls
  - Extract all tesseract word tokens with bounding boxes
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
  - tesserocr
  - Pillow
  - src/observation/color_isolate.py
"""

import re
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI, PSM, RIL

from src.observation.color_isolate import ColorIsolator


class BaseOCR:

    whitelist = '0123456789'
    outlier_threshold = float('inf')
    orientation = 'vertical'
    psm = PSM.SPARSE_TEXT

    def __init__(self, isolator: ColorIsolator = None):
        self.isolator = isolator or ColorIsolator()
        self._api = PyTessBaseAPI(path='/opt/homebrew/share/tessdata', psm=self.psm)
        self._api.SetVariable('tessedit_char_whitelist', self.whitelist)

    def __del__(self):
        try:
            self._api.End()
        except Exception:
            pass

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
        pil_img = Image.fromarray(mask)

        self._api.SetImage(pil_img)
        self._api.Recognize()

        h, w = mask.shape[:2]
        mid = h / 2 if self.orientation == 'vertical' else w / 2

        best_token, best_dist = None, float('inf')

        ri = self._api.GetIterator()
        if ri is None:
            return None

        level = RIL.WORD
        while True:
            try:
                text = (ri.GetUTF8Text(level) or '').strip()
                conf = ri.Confidence(level)
            except RuntimeError:
                text = ''
                conf = -1
            if text and conf >= 0:
                bbox = ri.BoundingBox(level)
                if bbox is not None:
                    x1, y1, x2, y2 = bbox
                    center = (y1 + y2) / 2 if self.orientation == 'vertical' else (x1 + x2) / 2
                    dist = abs(center - mid)
                    if dist < best_dist:
                        best_dist = dist
                        best_token = text
            if not ri.Next(level):
                break

        return best_token

    def _token_to_value(self, token: str) -> float | None:
        cleaned = re.sub(r'[^0-9.\-]', '', token)
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None