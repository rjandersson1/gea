"""
observation/ocr/heading.py

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

    def parse(self, img) -> float | None:
        """
        Extract centre heading value from tape.

        Returns:
            Heading in degrees [0, 360), or None on failure
        """
        pass

    def _cardinal_to_degrees(self, token: str) -> float | None:
        """Convert N/S/E/W string to degrees. Returns None if not cardinal."""
        pass
