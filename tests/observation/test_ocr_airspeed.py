"""
tests/observation/test_ocr_airspeed.py

Tests for src/observation/ocr/airspeed.py

Test cases:
  - parse returns float > 0 for valid synthetic images
  - parse returns None for blank image
  - outlier value (e.g. 9999) → None
  - accuracy on synthetic test set: MAE < 5 knots
"""

import pytest
import numpy as np

from src.observation.ocr.airspeed import AirspeedParser
