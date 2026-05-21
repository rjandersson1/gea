"""
tests/observation/test_ocr_altitude.py

Tests for src/observation/ocr/altitude.py

Test cases:
  - parse returns float >= 0 for valid synthetic images
  - parse returns None for blank image
  - outlier value → None
  - accuracy on synthetic test set: MAE < 10 feet
"""

import pytest
import numpy as np

from src.observation.ocr.altitude import AltitudeParser
