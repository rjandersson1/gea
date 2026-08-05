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
  - Interpolate between labelled ticks from the anchor token's pixel
    offset relative to the ROI centre

Subclass contract:
  - whitelist:            str, tesseract char whitelist
  - outlier_threshold:    float, reject abs(value) above this
  - orientation:          'vertical' (values stacked top-to-bottom) or
                          'horizontal' (values spaced left-to-right)
  - pixels_per_unit:      float|None, calibrated px per field unit.
                          None disables interpolation (anchor value only)
  - label_spacing_units:  float|None, nominal spacing between adjacent
                          labels, in field units. Sets the clamp limit
  - override _token_to_value() for non-numeric tokens (e.g. cardinals)
  - override _postprocess_value() for wraparound etc.

Sign convention:
  horizontal:  right = positive
  vertical:    up = positive (image y grows downward, so sign is flipped)

Dependencies:
  - numpy
  - opencv-python
  - tesserocr
  - Pillow
  - src/observation/color_isolate.py
  - src/observation/ocr/types.py
"""

import re
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI, PSM, RIL

from src.observation.color_isolate import ColorIsolator
from src.observation.ocr.types import OCRReading


class BaseOCR:

    whitelist = '0123456789'
    outlier_threshold = float('inf')
    orientation = 'vertical'
    psm = PSM.SPARSE_TEXT

    pixels_per_unit = None
    label_spacing_units = None

    def __init__(self, isolator: ColorIsolator = None):
        self.isolator = isolator or ColorIsolator()
        self._api = PyTessBaseAPI(path='/opt/homebrew/share/tessdata', psm=self.psm)
        self._api.SetVariable('tessedit_char_whitelist', self.whitelist)

    def __del__(self):
        try:
            self._api.End()
        except Exception:
            pass

    def parse(self, img: np.ndarray) -> OCRReading:
        mask = self._preprocess(img)
        result = self._extract_centre_token(mask)
        if result is None:
            return OCRReading()

        token, bbox = result
        anchor_value = self._token_to_value(token)
        if anchor_value is None:
            return OCRReading(anchor_token=token)
        if abs(anchor_value) > self.outlier_threshold:
            return OCRReading(anchor_token=token)

        reading = OCRReading(
            value=self._postprocess_value(anchor_value),
            anchor_token=token,
            anchor_value=anchor_value,
        )

        if self.pixels_per_unit is None:
            return reading

        offset_px, clamped = self._compute_offset(bbox, mask.shape)
        offset_units = offset_px / self.pixels_per_unit

        reading.offset_px = offset_px
        reading.offset_units = offset_units
        reading.clamped = clamped
        reading.value = self._postprocess_value(anchor_value + offset_units)
        return reading

    def _preprocess(self, img: np.ndarray) -> np.ndarray:
        return self.isolator.isolate(img)

    def _extract_tokens(self, mask: np.ndarray, level=RIL.WORD) -> list:
        """Return [(text, bbox, conf), ...] for all recognised tokens."""
        pil_img = Image.fromarray(mask)

        self._api.SetImage(pil_img)
        self._api.Recognize()

        tokens = []
        ri = self._api.GetIterator()
        if ri is None:
            return tokens

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
                    tokens.append((text, bbox, conf))
            if not ri.Next(level):
                break

        return tokens

    def _extract_centre_token(self, mask: np.ndarray) -> tuple | None:
        tokens = self._extract_tokens(mask)
        if not tokens:
            return None

        h, w = mask.shape[:2]
        mid = h / 2 if self.orientation == 'vertical' else w / 2

        best_token, best_bbox, best_dist = None, None, float('inf')
        for text, bbox, _conf in tokens:
            x1, y1, x2, y2 = bbox
            center = (y1 + y2) / 2 if self.orientation == 'vertical' else (x1 + x2) / 2
            dist = abs(center - mid)
            if dist < best_dist:
                best_dist = dist
                best_token = text
                best_bbox = bbox

        if best_token is None:
            return None
        return best_token, best_bbox

    def _compute_offset(self, bbox, mask_shape) -> tuple:
        x1, y1, x2, y2 = bbox
        h, w = mask_shape[:2]

        if self.orientation == 'vertical':
            offset_px = ((y1 + y2) / 2) - (h / 2)
        else:
            offset_px = (w / 2) - ((x1 + x2) / 2)

        clamped = False
        if self.label_spacing_units is not None:
            limit = (self.label_spacing_units / 2.0) * self.pixels_per_unit
            if offset_px > limit:
                offset_px = limit
                clamped = True
            elif offset_px < -limit:
                offset_px = -limit
                clamped = True

        return offset_px, clamped

    def _postprocess_value(self, value: float) -> float:
        return value

    def _token_to_value(self, token: str) -> float | None:
        cleaned = re.sub(r'[^0-9.\-]', '', token)
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None