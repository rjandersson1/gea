"""
tests/observation/test_ocr_heading.py

Tests for src/observation/ocr/heading.py

Test cases:
  - parse returns float in [0, 360) for valid synthetic images
  - parse returns None for blank image
  - parse returns None for image with no recognisable digits
  - cardinal N → 0.0
  - cardinal E → 90.0
  - cardinal S → 180.0
  - cardinal W → 270.0
  - outlier value (e.g. 999) → None
  - accuracy on synthetic test set: MAE < 2 degrees
"""

import pytest
import numpy as np

from src.observation.ocr.heading import HeadingParser
