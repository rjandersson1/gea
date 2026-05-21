"""
tests/observation/test_capture.py

Tests for src/observation/capture.py

Test cases:
  - grab_full returns numpy array with 3 channels
  - grab_roi returns correct shape given rois.yaml coords
  - grab_roi raises KeyError for unknown roi_name
  - save_raw writes a file to the given path

Note: these tests require a display/screen to be available.
Skip on headless CI with:  @pytest.mark.skipif(...)
"""

import pytest
import numpy as np

from src.observation.capture import ScreenCapture
