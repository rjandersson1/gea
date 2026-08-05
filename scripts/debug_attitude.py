"""
scripts/debug_attitude.py

Visual debug tool for AttitudeParser (phase 0).

Renders, for a single frame:
  - the isolated mask
  - elongated components accepted as rung segments (blue), with the
    inlier set used for the roll estimate highlighted
  - detected label groups (orange boxes) and their OCR values
  - the fitted roll axis through the ROI centre (green)
  - rung s-clusters used for the pixels-per-degree calibration

Usage:
    python scripts/debug_attitude.py <image_path> [--mask-mode color|gray]
    python scripts/debug_attitude.py --sweep <folder>    # metrics over a set

--mask-mode gray thresholds on brightness instead of HUD-green, for
schematic/mock images. Real captures should use color.

Dependencies:
  - opencv-python
  - numpy
  - src/observation/color_isolate.py
  - src/observation/ocr/attitude.py
  - src/utils/config.py
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np

from src.utils.config import load_config, get_project_root
from src.observation.color_isolate import ColorIsolator
from src.observation.ocr.attitude import AttitudeParser


class GrayIsolator:
    """Threshold stand-in for ColorIsolator, for mock/schematic images."""

    def isolate(self, img_bgr: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        return (gray > 0).astype(np.uint8) * 255


def crop_roi(img, roi):
    return img[roi['y1']:roi['y2'], roi['x1']:roi['x2']]


def render(parser, crop, scale=3):
    mask = parser._preprocess(crop)
    h_ref = parser._glyph_scale(mask)
    roll, n_segs = parser._estimate_roll(mask, h_ref)
    labels = parser._extract_labels(mask, h_ref)
    if labels:
        parser._read_values(mask, labels)
    reading = parser.parse(crop)

    vis = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    vis = cv2.resize(vis, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
    h, w = mask.shape[:2]
    cx, cy = w / 2.0, h / 2.0

    cv2.line(vis, (int(cx * scale), 0), (int(cx * scale), h * scale), (70, 70, 70), 1)
    cv2.line(vis, (0, int(cy * scale)), (w * scale, int(cy * scale)), (70, 70, 70), 1)

    for label in labels:
        x1, y1, x2, y2 = label['bbox']
        cv2.rectangle(vis, (x1 * scale, y1 * scale), (x2 * scale, y2 * scale),
                      (0, 150, 255), 1)
        if label['value'] is not None:
            cv2.putText(vis, f"{label['value']:g}",
                        (x1 * scale, max(10, y1 * scale - 3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 200, 255), 1)

    if roll is not None:
        theta = np.radians(roll)
        dx, dy = np.cos(theta) * w, np.sin(theta) * w
        p0 = (int((cx - dx) * scale), int((cy - dy) * scale))
        p1 = (int((cx + dx) * scale), int((cy + dy) * scale))
        cv2.line(vis, p0, p1, (0, 255, 0), 2)

    roll_txt = 'None' if reading.roll is None else f'{reading.roll:+.2f}'
    pitch_txt = 'None' if reading.pitch is None else f'{reading.pitch:+.2f}'
    ppu_txt = 'None' if reading.pixels_per_unit is None else f'{reading.pixels_per_unit:.2f}'
    cv2.putText(vis, f'roll={roll_txt}  pitch={pitch_txt}', (5, 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    cv2.putText(vis, f'ppu={ppu_txt} segs={n_segs} labels={len(labels)}', (5, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 200, 200), 1)
    return vis, reading, labels, n_segs


def sweep(parser, root, folder, roi):
    frames_dir = os.path.join(root, 'data', 'screenshots', folder)
    names = sorted(f for f in os.listdir(frames_dir) if f.endswith('.png'))
    rolls, pitches, ppus = [], [], []
    for name in names:
        img = cv2.imread(os.path.join(frames_dir, name))
        if img is None:
            continue
        r = parser.parse(crop_roi(img, roi))
        rolls.append(np.nan if r.roll is None else r.roll)
        pitches.append(np.nan if r.pitch is None else r.pitch)
        if r.pixels_per_unit is not None:
            ppus.append(r.pixels_per_unit)

    rolls = np.array(rolls, dtype=float)
    pitches = np.array(pitches, dtype=float)
    d = (np.diff(rolls) + 90) % 180 - 90
    d = np.abs(d[~np.isnan(d)])
    pd = np.abs(np.diff(pitches))
    pd = pd[~np.isnan(pd)]

    print(f'frames            {len(rolls)}')
    print(f'roll  dropout     {100 * np.isnan(rolls).mean():.1f}%')
    print(f'roll  med|delta|  {np.median(d):.2f} deg   p90 {np.percentile(d, 90):.2f}')
    print(f'roll  >20deg jump {100 * (d > 20).mean():.1f}%')
    print(f'pitch dropout     {100 * np.isnan(pitches).mean():.1f}%')
    if len(pd):
        print(f'pitch med|delta|  {np.median(pd):.2f} deg   p90 {np.percentile(pd, 90):.2f}')
    if ppus:
        print(f'ppu   median      {np.median(ppus):.2f} px/deg  '
              f'iqr {np.percentile(ppus, 25):.2f}-{np.percentile(ppus, 75):.2f}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('target')
    ap.add_argument('--sweep', action='store_true')
    ap.add_argument('--mask-mode', choices=['color', 'gray'], default='color')
    ap.add_argument('--scale', type=int, default=3)
    ap.add_argument('--out', default='data/screenshots/debug/attitude_debug.png')
    args = ap.parse_args()

    root = get_project_root()
    roi = load_config(os.path.join(root, 'config', 'rois.yaml'))['attitude_indicator']
    isolator = ColorIsolator() if args.mask_mode == 'color' else GrayIsolator()
    parser = AttitudeParser(isolator=isolator)

    if args.sweep:
        sweep(parser, root, args.target, roi)
        return

    img = cv2.imread(args.target)
    if img is None:
        print(f'could not read {args.target}')
        return
    vis, reading, labels, n_segs = render(parser, crop_roi(img, roi), args.scale)

    print(f'roll   {reading.roll}')
    print(f'pitch  {reading.pitch}   anchor={reading.anchor_value}')
    print(f'ppu    {reading.pixels_per_unit}')
    print(f'segs   {n_segs}   labels {len(labels)}')
    for label in labels:
        print(f"   bbox={label['bbox']} token={label['token']!r} "
              f"value={label['value']} conf={label['conf']}")

    out_path = os.path.join(root, args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, vis)
    print(f'saved: {out_path}')


if __name__ == '__main__':
    main()
