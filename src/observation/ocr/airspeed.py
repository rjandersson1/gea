"""
src/observation/ocr/airspeed.py

Responsibilities:
  - Parse current airspeed from the airspeed tape ROI (left side of HUD)
  - Tape shows multiple values; extract centre (current) value only
  - Output units: knots (as displayed by GE)
  - Plausible range SR22: 60–200 kts, F-16: 100–800 kts

Dependencies:
  - src/observation/ocr/base.py
"""

from src.observation.ocr.base import BaseOCR


class AirspeedParser(BaseOCR):

    whitelist = '0123456789'
    outlier_threshold = 900.0
    orientation = 'vertical'