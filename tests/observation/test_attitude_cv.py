"""
tests/observation/test_attitude_cv.py

Tests for src/observation/cv/attitude.py and src/observation/cv/hough.py

Test cases (hough.py):
  - find_lines returns list of Line objects
  - find_horizontal_lines filters correctly at given angle_tol
  - line_angle returns 0.0 for a perfectly horizontal line
  - line_angle returns correct sign for clockwise vs anticlockwise tilt
  - line_length returns correct Euclidean length

Test cases (attitude.py):
  - estimate returns dict with 'bank' and 'pitch' keys
  - bank=0 for image with horizontal zero-pitch line
  - bank sign: positive for clockwise rotation
  - estimate returns {'bank': None, 'pitch': None} for blank image
"""

import pytest
import numpy as np

from src.observation.cv.hough import find_lines, find_horizontal_lines, line_angle, Line
from src.observation.cv.attitude import AttitudeEstimator
