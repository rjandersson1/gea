"""
scripts/test_ocr_on_set.py

Responsibilities:
  - Load all frames from data/screenshots/test_set/
  - Load ROI boxes from config/rois.yaml
  - Load truth values from data/screenshots/test_set/labels.csv (if present)
  - Crop each frame to heading/airspeed/altitude ROIs
  - Run corresponding parser on each crop, print value + latency + error vs truth
  - Print summary latency and accuracy stats per field across all frames
  - Manual visual sanity check against known frame values — not pass/fail

Usage:
    python scripts/test_ocr_on_set.py

Dependencies:
  - opencv-python
  - pyyaml
  - numpy
  - src/utils/config.py
  - src/observation/ocr/heading.py
  - src/observation/ocr/airspeed.py
  - src/observation/ocr/altitude.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
import time
import cv2
import yaml
import numpy as np

from src.utils.config import get_project_root
from src.observation.ocr.heading import HeadingParser
from src.observation.ocr.airspeed import AirspeedParser
from src.observation.ocr.altitude import AltitudeParser


PARSERS = {
    'heading_tape': HeadingParser(),
    'airspeed_tape': AirspeedParser(),
    'altitude_tape': AltitudeParser(),
}


def crop_image(img, roi: dict):
    return img[roi['y1']:roi['y2'], roi['x1']:roi['x2']]


def _load_labels(path: str) -> dict:
    if not os.path.exists(path):
        print(f"no labels.csv found at {path} — skipping truth comparison")
        return {}
    labels = {}
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            labels[row['frame']] = row
    return labels


def _parse_truth(raw: str):
    raw = (raw or '').strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def main():
    root = get_project_root()
    test_set_dir = os.path.join(root, 'data', 'screenshots', 'test_set')
    rois_path = os.path.join(root, 'config', 'rois.yaml')
    labels_path = os.path.join(test_set_dir, 'labels.csv')

    with open(rois_path) as f:
        rois = yaml.safe_load(f)

    labels = _load_labels(labels_path)

    frames = sorted(f for f in os.listdir(test_set_dir) if f.endswith('.png'))
    if not frames:
        print(f"no frames found in {test_set_dir}")
        return

    latencies_ms = {name: [] for name in PARSERS}
    errors = {name: [] for name in PARSERS}

    for frame_name in frames:
        img = cv2.imread(os.path.join(test_set_dir, frame_name))
        print(f"\n{frame_name}")
        truth_row = labels.get(frame_name, {})

        for roi_name, parser in PARSERS.items():
            if roi_name not in rois:
                print(f"  {roi_name}: ROI missing from rois.yaml")
                continue
            crop = crop_image(img, rois[roi_name])

            t0 = time.perf_counter()
            value = parser.parse(crop)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            latencies_ms[roi_name].append(elapsed_ms)

            truth = _parse_truth(truth_row.get(roi_name))
            if truth is None:
                print(f"  {roi_name}: {value}  ({elapsed_ms:.1f} ms)  [no truth]")
            elif value is None:
                print(f"  {roi_name}: {value}  ({elapsed_ms:.1f} ms)  truth={truth}  MISS")
                errors[roi_name].append(None)
            else:
                err = value - truth
                errors[roi_name].append(err)
                print(f"  {roi_name}: {value}  ({elapsed_ms:.1f} ms)  truth={truth}  err={err:+.1f}")

    total_per_frame_ms = sum(np.mean(v) for v in latencies_ms.values() if v)

    print("\n--- latency summary (ms) ---")
    for name, samples in latencies_ms.items():
        if not samples:
            continue
        arr = np.array(samples)
        print(
            f"  {name}: mean={arr.mean():.1f}  "
            f"p95={np.percentile(arr, 95):.1f}  "
            f"max={arr.max():.1f}  n={len(arr)}"
        )
    print(f"\n  sum of per-field means: {total_per_frame_ms:.1f} ms/frame")
    if total_per_frame_ms > 0:
        print(f"  implied max sequential rate: {1000.0 / total_per_frame_ms:.1f} Hz")

    print("\n--- accuracy summary ---")
    for name, errs in errors.items():
        valid = [e for e in errs if e is not None]
        n_miss = len(errs) - len(valid)
        if valid:
            arr = np.array(valid)
            mae = np.mean(np.abs(arr))
            print(f"  {name}: MAE={mae:.1f}  n={len(valid)}  dropouts={n_miss}")
        else:
            print(f"  {name}: no valid comparisons  dropouts={n_miss}")


if __name__ == '__main__':
    main()