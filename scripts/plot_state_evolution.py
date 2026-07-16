"""
scripts/plot_state_evolution.py

Responsibilities:
  - Run OCR over an ordered sequence of frames (e.g. data/screenshots/test_flight_10s/)
  - Assemble heading/airspeed/altitude time series (None -> NaN, gaps visible)
  - Plot one figure, one subplot per field, x-axis in seconds from capture start
  - Save figure to data/screenshots/state_evolution.png

Usage:
    python scripts/plot_state_evolution.py [folder_name]

    folder_name defaults to 'test_flight_10s', relative to data/screenshots/

Dependencies:
  - opencv-python
  - pyyaml
  - numpy
  - matplotlib
  - src/utils/config.py
  - src/observation/ocr/heading.py
  - src/observation/ocr/airspeed.py
  - src/observation/ocr/altitude.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import yaml
import numpy as np
import matplotlib.pyplot as plt

from src.utils.config import get_project_root
from src.observation.ocr.heading import HeadingParser
from src.observation.ocr.airspeed import AirspeedParser
from src.observation.ocr.altitude import AltitudeParser


PARSERS = {
    'heading_tape': HeadingParser(),
    'airspeed_tape': AirspeedParser(),
    'altitude_tape': AltitudeParser(),
}

CAPTURE_HZ = 10.0


def crop_image(img, roi: dict):
    return img[roi['y1']:roi['y2'], roi['x1']:roi['x2']]


def main():
    root = get_project_root()
    folder_name = sys.argv[1] if len(sys.argv) > 1 else 'test_flight_10s'
    frames_dir = os.path.join(root, 'data', 'screenshots', folder_name)
    rois_path = os.path.join(root, 'config', 'rois.yaml')

    with open(rois_path) as f:
        rois = yaml.safe_load(f)

    frames = sorted(f for f in os.listdir(frames_dir) if f.endswith('.png'))
    if not frames:
        print(f"no frames found in {frames_dir}")
        return

    series = {name: [] for name in PARSERS}

    for frame_name in frames:
        img = cv2.imread(os.path.join(frames_dir, frame_name))
        for roi_name, parser in PARSERS.items():
            if roi_name not in rois:
                series[roi_name].append(np.nan)
                continue
            crop = crop_image(img, rois[roi_name])
            value = parser.parse(crop)
            series[roi_name].append(value if value is not None else np.nan)

    n = len(frames)
    t = np.arange(n) / CAPTURE_HZ

    fig, axes = plt.subplots(len(PARSERS), 1, figsize=(10, 8), sharex=True)
    if len(PARSERS) == 1:
        axes = [axes]

    for ax, (name, values) in zip(axes, series.items()):
        arr = np.array(values, dtype=float)
        ax.plot(t, arr, marker='.', linewidth=1)
        ax.set_ylabel(name)
        ax.grid(True, alpha=0.3)
        n_dropout = np.isnan(arr).sum()
        if n_dropout:
            ax.set_title(f"{n_dropout} dropout(s)", fontsize=9, loc='right', color='red')

    axes[-1].set_xlabel('time (s)')
    fig.suptitle(f'state evolution — {folder_name} ({n} frames)')
    fig.tight_layout()

    out_path = os.path.join(root, 'data', 'screenshots', 'state_evolution.png')
    fig.savefig(out_path, dpi=150)
    print(f"saved plot to {out_path}")
    plt.show()


if __name__ == '__main__':
    main()