"""
src/observation/ocr/heading.py

Responsibilities:
  - Parse current heading from the heading tape ROI
  - Heading tape shows e.g. '30  33  N' — extract centre value
  - Handle cardinal labels (N=0, E=90, S=180, W=270)
  - Output range: 0.0–360.0 degrees

Dependencies:
  - src/observation/ocr/base.py
"""

from src.observation.ocr.base import BaseOCR


class HeadingParser(BaseOCR):

    whitelist = '0123456789NSEW '
    outlier_threshold = 360.0
    orientation = 'horizontal'

    CARDINAL_DEGREES = {'N': 0.0, 'E': 90.0, 'S': 180.0, 'W': 270.0}

    def parse(self, img) -> float | None:
        value = super().parse(img)
        if value is None:
            return None
        return value % 360.0

    def _token_to_value(self, token: str) -> float | None:
        cardinal = self._cardinal_to_degrees(token)
        if cardinal is not None:
            return cardinal
        return super()._token_to_value(token)

    def _cardinal_to_degrees(self, token: str) -> float | None:
        return self.CARDINAL_DEGREES.get(token.strip().upper())