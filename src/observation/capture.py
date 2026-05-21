"""
observation/capture.py

Responsibilities:
  - Capture full screenshots of the GE window using mss
  - Crop to named ROIs defined in config/rois.yaml
  - Save raw screenshots to data/screenshots/raw/ for calibration
  - All downstream parsers receive cropped ROI images from here

Dependencies:
  - mss
  - numpy
  - src/utils/config.py    (loads rois.yaml)
"""

import numpy as np
import mss

from src.utils.config import load_config


class ScreenCapture:

    def __init__(self, rois_config_path: str):
        """
        Args:
            rois_config_path: path to config/rois.yaml
        """
        pass

    def grab_full(self) -> np.ndarray:
        """Capture full screen. Returns HxWx3 RGB numpy array."""
        pass

    def grab_roi(self, roi_name: str) -> np.ndarray:
        """
        Capture and crop to named ROI from rois.yaml.

        Args:
            roi_name: key in rois.yaml e.g. 'heading_tape'

        Returns:
            Cropped HxWx3 RGB numpy array
        """
        pass

    def save_raw(self, path: str) -> None:
        """Save the last full screenshot to path. For calibration/debugging."""
        pass
