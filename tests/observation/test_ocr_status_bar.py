"""
tests/observation/test_ocr_status_bar.py

Tests for src/observation/ocr/status_bar.py

Test cases:
  - parse returns dict with 'eye_alt' key
  - eye_alt is float for valid status bar image
  - eye_alt is None for blank image
  - regex correctly ignores lat/lon/elev fields
  - units: metres parsed correctly (e.g. '258 m' → 258.0)
"""

import pytest
import numpy as np

from src.observation.ocr.status_bar import StatusBarParser
