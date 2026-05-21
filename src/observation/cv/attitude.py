"""
observation/cv/attitude.py

Responsibilities:
  - Estimate bank and pitch angles from the attitude indicator ROI
  - Bank:  angle of the pitch=0 line from horizontal
           positive = right wing down
  - Pitch: vertical offset of pitch=0 line from ROI centre
           scaled by known pixel-per-degree calibration factor
  - Uses color isolation to isolate HUD green before line detection
  - Uses hough.find_horizontal_lines to locate the pitch=0 line
    (longest near-horizontal line in the attitude ROI)

Dependencies:
  - numpy
  - src/observation/color_isolate.py
  - src/observation/cv/hough.py
"""

import numpy as np

from src.observation.color_isolate import ColorIsolator
from src.observation.cv.hough import find_horizontal_lines, line_angle


class AttitudeEstimator:

    def __init__(self, isolator: ColorIsolator, pixels_per_degree: float = None):
        """
        Args:
            isolator:           ColorIsolator instance
            pixels_per_degree:  pitch scaling factor — calibrate empirically
                                if None, pitch returned as pixel offset only
        """
        pass

    def estimate(self, img: np.ndarray) -> dict:
        """
        Estimate bank and pitch from attitude indicator ROI image.

        Returns:
            dict with keys:
              'bank':  float|None  degrees, positive = right wing down
              'pitch': float|None  degrees positive = nose up
        """
        pass

    def _find_zero_pitch_line(self, img: np.ndarray):
        """
        Isolate image, detect lines, return longest near-horizontal line.
        This corresponds to the pitch=0 ladder line.
        """
        pass

    def _bank_from_line(self, line) -> float:
        """Extract bank angle from line angle."""
        pass

    def _pitch_from_line(self, line, roi_height: int) -> float | None:
        """
        Estimate pitch from vertical position of zero-pitch line
        relative to ROI centre.
        """
        pass
