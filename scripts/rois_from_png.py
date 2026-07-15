"""
scripts/rois_from_png.py

Responsibilities:
  - Read a PNG with filled ROI boxes hand-drawn in per-field colors
  - For each defined color, find the bounding box of matching pixels
  - Write resulting boxes to config/rois.yaml
  - Pixels in the source PNG correspond 1:1 to window coordinates

Usage:
    python scripts/rois_from_png.py

Dependencies:
  - opencv-python
  - numpy
  - pyyaml
  - src/utils/config.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
import yaml

from src.utils.config import get_project_root


INPUT_PNG_PATH = '/Users/rja/Documents/Coding/gea/data/screenshots/test_set_roi/roi_def.png'

# BGR, matching cv2's channel order — not RGB
ROI_COLORS_BGR = {
    'heading_tape':       (255, 255, 0),    # cyan
    'airspeed_tape':      (0, 0, 255),      # red
    'altitude_tape':      (0, 255, 0),      # green
    'attitude_indicator': (0, 255, 255),    # yellow
    'status_bar':         (255, 0, 255),    # magenta
}

COLOR_TOLERANCE = 20


def find_box_for_color(img_bgr: np.ndarray, target_bgr: tuple, tol: int) -> dict | None:
    lower = np.array([max(c - tol, 0) for c in target_bgr])
    upper = np.array([min(c + tol, 255) for c in target_bgr])
    mask = cv2.inRange(img_bgr, lower, upper)

    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return None

    return {
        'x1': int(xs.min()),
        'y1': int(ys.min()),
        'x2': int(xs.max()) + 1,
        'y2': int(ys.max()) + 1,
    }


def main():
    if not os.path.exists(INPUT_PNG_PATH):
        print(f"input PNG not found: {INPUT_PNG_PATH}")
        return

    img = cv2.imread(INPUT_PNG_PATH)
    if img is None:
        print(f"failed to load image: {INPUT_PNG_PATH}")
        return

    rois = {}
    for name, color in ROI_COLORS_BGR.items():
        box = find_box_for_color(img, color, COLOR_TOLERANCE)
        if box is None:
            print(f"warning: no pixels found for {name} (color {color})")
            continue
        rois[name] = box
        print(f"{name}: {box}")

    missing = set(ROI_COLORS_BGR.keys()) - set(rois.keys())
    if missing:
        print(f"\nwarning: missing ROIs, not written: {missing}")

    root = get_project_root()
    out_path = os.path.join(root, 'config', 'rois.yaml')
    with open(out_path, 'w') as f:
        yaml.safe_dump(rois, f)
    print(f"\nrois saved to {out_path}")


if __name__ == '__main__':
    main()