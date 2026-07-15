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
import mss.tools
from pathlib import Path
from AppKit import NSWorkspace
from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID


from src.utils.config import load_config







class ScreenCapture:

    def __init__(self, rois_config_path: str):
        """
        Args:
            rois_config_path: path to config/rois.yaml
        """
        self.get_ge_window_rect()
        self.calibrate()
        pass

    def calibrate(self) -> None:
        """Capture a test screenshot and save to data/screenshots/calibration.png."""
        left, top, width, height = self.get_ge_window_rect()
        output_path = Path(__file__).resolve().parents[2] / "data/screenshots/calibration.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with mss.mss() as screen:
            screenshot = screen.grab({
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            })
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(output_path))


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

    def get_ge_window_rect() -> tuple:
        """Returns (left, top, width, height) of the Google Earth window."""
        windows = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        for w in windows:
            if 'Google Earth' in w.get('kCGWindowOwnerName', ''):
                bounds = w['kCGWindowBounds']
                return (
                    int(bounds['X']),
                    int(bounds['Y']),
                    int(bounds['Width']),
                    int(bounds['Height'])
                )
        raise RuntimeError('Google Earth window not found — is it open?')
