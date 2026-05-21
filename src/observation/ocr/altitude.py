"""
observation/ocr/altitude.py

Responsibilities:
  - Parse current altitude from the altitude tape ROI (right side of HUD)
  - Tape shows multiple values; extract centre (current) value only
  - Output units: feet MSL (as displayed by GE)
  - Plausible range: 0–50000 ft

Dependencies:
  - src/observation/ocr/base.py
"""

from src.observation.ocr.base import BaseOCR


class AltitudeParser(BaseOCR):

    whitelist = '0123456789'
    outlier_threshold = 60000.0

    def parse(self, img) -> float | None:
        """
        Extract centre altitude value from tape.

        Returns:
            Altitude in feet MSL, or None on failure
        """
        pass
