"""
src/observation/ocr/altitude.py

Responsibilities:
  - Parse current altitude from the altitude tape ROI (right side of HUD)
  - Tape shows multiple values; extract centre (current) value only
  - Output units: feet (as displayed by GE)

Dependencies:
  - src/observation/ocr/base.py
"""

from src.observation.ocr.base import BaseOCR


class AltitudeParser(BaseOCR):

    whitelist = '0123456789'
    outlier_threshold = 60000.0
    orientation = 'vertical'