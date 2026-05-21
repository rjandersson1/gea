"""
tests/observation/test_color_isolate.py

Tests for src/observation/color_isolate.py

Test cases:
  - get_mask: pure target color pixel → True
  - get_mask: pixel outside margin → False
  - get_mask: pixel at exact margin boundary → True
  - get_mask: dilation radius=0 gives no expansion
  - get_mask: dilation radius=2 expands mask by expected amount
  - isolate: non-masked pixels are zeroed
  - isolate: masked pixels retain original color
  - from_config: loads correctly from ocr.yaml
"""

import pytest
import numpy as np

from src.observation.color_isolate import ColorIsolator
