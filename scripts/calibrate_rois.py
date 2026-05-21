"""
scripts/calibrate_rois.py

Responsibilities:
  - Interactive tool to define ROI pixel coordinates for all HUD elements
  - Takes a screenshot of the current screen
  - Opens it in a matplotlib window
  - User clicks two corners (top-left, bottom-right) for each named ROI
  - Saves results to config/rois.yaml
  - Run once on PC with GE open in flight sim mode before any OCR dev

Usage:
    python scripts/calibrate_rois.py

ROIs to calibrate (in order):
    heading_tape, airspeed_tape, altitude_tape,
    attitude_indicator, status_bar

Dependencies:
  - mss
  - matplotlib
  - numpy
  - pyyaml
  - src/utils/config.py
"""

import mss
import numpy as np
import matplotlib.pyplot as plt
import yaml
import os

from src.utils.config import get_project_root


ROI_NAMES = [
    'heading_tape',
    'airspeed_tape',
    'altitude_tape',
    'attitude_indicator',
    'status_bar',
]


def capture_screen() -> np.ndarray:
    """Capture full screen and return as numpy array."""
    pass


def select_roi(img: np.ndarray, roi_name: str) -> dict:
    """
    Display img and prompt user to click two corners.
    Returns dict with keys x1, y1, x2, y2.
    """
    pass


def main():
    """Run calibration for all ROI_NAMES and save to config/rois.yaml."""
    pass


if __name__ == '__main__':
    main()
