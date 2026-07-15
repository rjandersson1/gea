"""
scripts/calibrate_rois.py

Responsibilities:
  - Find the GE window by title/owner (Mac: Quartz)
  - Screenshot just that window region
  - Auto-detect ROIs via HUD-green color isolation + column/row band analysis
    (uses horizontal centering of heading/attitude vs left/right tapes)
  - Status bar detected separately (not HUD green) via fixed bottom-strip heuristic
  - Draw red debug boxes over detected ROIs, save for visual tuning
  - Save detected coordinates to config/rois.yaml

Usage:
    python scripts/calibrate_rois.py

Dependencies:
  - mss
  - opencv-python
  - numpy
  - pyyaml
  - pyobjc-framework-Quartz   (Mac only — window enumeration)
  - src/utils/config.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2
import mss
import yaml
import Quartz

from src.utils.config import get_project_root


ROI_NAMES = [
    'heading_tape',
    'airspeed_tape',
    'altitude_tape',
    'attitude_indicator',
    'status_bar',
]

HUD_COLOR_BGR = (0, 251, 0)
COLOR_MARGIN = 100

COLUMN_GAP_TOL = 30
ROW_GAP_TOL = 25
CENTER_TOL_FRAC = 0.12

HEADING_MARGIN = 10
ATTITUDE_MARGIN = 15
AIRSPEED_MARGIN = 10
ALTITUDE_MARGIN = 10

STATUS_BAR_HEIGHT_FRAC = 0.035


def find_window(title_substring: str = 'Google Earth') -> dict:
    window_list = Quartz.CGWindowListCopyWindowInfo(
        Quartz.kCGWindowListOptionOnScreenOnly,
        Quartz.kCGNullWindowID
    )
    for w in window_list:
        owner = w.get('kCGWindowOwnerName', '') or ''
        title = w.get('kCGWindowName', '') or ''
        if title_substring.lower() in owner.lower() or title_substring.lower() in title.lower():
            bounds = w['kCGWindowBounds']
            return {
                'x': int(bounds['X']),
                'y': int(bounds['Y']),
                'width': int(bounds['Width']),
                'height': int(bounds['Height']),
            }
    raise RuntimeError(f"no window found matching '{title_substring}'")


def screenshot_window(bounds: dict) -> np.ndarray:
    with mss.mss() as sct:
        region = {
            'left': bounds['x'],
            'top': bounds['y'],
            'width': bounds['width'],
            'height': bounds['height'],
        }
        raw = np.array(sct.grab(region))
    return raw[:, :, :3]


def _isolate_hud_color(img_bgr: np.ndarray) -> np.ndarray:
    lower = np.array([max(c - COLOR_MARGIN, 0) for c in HUD_COLOR_BGR])
    upper = np.array([min(c + COLOR_MARGIN, 255) for c in HUD_COLOR_BGR])
    return cv2.inRange(img_bgr, lower, upper)


def _detect_status_bar(img_shape: tuple) -> dict:
    h, w = img_shape[:2]
    bar_h = int(h * STATUS_BAR_HEIGHT_FRAC)
    return {'x1': 0, 'y1': h - bar_h, 'x2': w, 'y2': h}


def _active_ranges(active: np.ndarray, gap_tol: int) -> list:
    idxs = np.where(active)[0]
    if len(idxs) == 0:
        return []
    ranges = []
    start = prev = idxs[0]
    for idx in idxs[1:]:
        if idx - prev > gap_tol:
            ranges.append((start, prev))
            start = idx
        prev = idx
    ranges.append((start, prev))
    return ranges


def _classify_column_bands(bands: list, img_w: int, center_tol_frac: float = CENTER_TOL_FRAC) -> dict:
    cx = img_w / 2
    zones = {}
    for (b0, b1) in bands:
        center = (b0 + b1) / 2
        if abs(center - cx) / img_w < center_tol_frac:
            zone = 'center'
        elif center < cx:
            zone = 'left'
        else:
            zone = 'right'
        if zone not in zones:
            zones[zone] = [b0, b1]
        else:
            zones[zone][0] = min(zones[zone][0], b0)
            zones[zone][1] = max(zones[zone][1], b1)
    return {z: tuple(v) for z, v in zones.items()}


def _largest_row_band(mask_slice: np.ndarray, gap_tol: int):
    bands = _active_ranges(mask_slice.sum(axis=1) > 0, gap_tol)
    if not bands:
        return None
    return max(bands, key=lambda b: b[1] - b[0])


def _pad_box(x1: int, y1: int, x2: int, y2: int, margin: int, img_shape: tuple) -> dict:
    h, w = img_shape
    return {
        'x1': int(max(x1 - margin, 0)),
        'y1': int(max(y1 - margin, 0)),
        'x2': int(min(x2 + margin, w)),
        'y2': int(min(y2 + margin, h)),
    }


def detect_rois(img_bgr: np.ndarray, debug: bool = False):
    mask = _isolate_hud_color(img_bgr)
    h, w = mask.shape[:2]

    col_bands = _active_ranges(mask.sum(axis=0) > 0, COLUMN_GAP_TOL)
    zone_cols = _classify_column_bands(col_bands, w)

    rois = {}
    center_row_bands = []

    if 'left' in zone_cols:
        x1, x2 = zone_cols['left']
        row_band = _largest_row_band(mask[:, x1:x2 + 1], ROW_GAP_TOL)
        if row_band:
            rois['airspeed_tape'] = _pad_box(x1, row_band[0], x2, row_band[1], AIRSPEED_MARGIN, (h, w))

    if 'right' in zone_cols:
        x1, x2 = zone_cols['right']
        row_band = _largest_row_band(mask[:, x1:x2 + 1], ROW_GAP_TOL)
        if row_band:
            rois['altitude_tape'] = _pad_box(x1, row_band[0], x2, row_band[1], ALTITUDE_MARGIN, (h, w))

    if 'center' in zone_cols:
        cx1, cx2 = zone_cols['center']
        center_row_bands = _active_ranges(mask[:, cx1:cx2 + 1].sum(axis=1) > 0, ROW_GAP_TOL)

        if center_row_bands:
            hy1, hy2 = center_row_bands[0]
            rois['heading_tape'] = _pad_box(cx1, hy1, cx2, hy2, HEADING_MARGIN, (h, w))

            if len(center_row_bands) > 1:
                ay1 = center_row_bands[1][0]
                ay2 = center_row_bands[-1][1]
                rois['attitude_indicator'] = _pad_box(cx1, ay1, cx2, ay2, ATTITUDE_MARGIN, (h, w))

    missing = set(ROI_NAMES) - {'status_bar'} - set(rois.keys())
    if missing:
        print(f"warning: could not detect zones: {missing}")

    rois['status_bar'] = _detect_status_bar((h, w))

    if debug:
        dbg = {
            'mask': mask,
            'col_bands': col_bands,
            'zone_cols': zone_cols,
            'center_row_bands': center_row_bands,
        }
        return rois, dbg
    return rois


def draw_debug_boxes(img_bgr: np.ndarray, rois: dict) -> np.ndarray:
    out = img_bgr.copy()
    for name, box in rois.items():
        cv2.rectangle(out, (box['x1'], box['y1']), (box['x2'], box['y2']), (0, 0, 255), 2)
        cv2.putText(out, name, (box['x1'], max(box['y1'] - 6, 0)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    return out


def draw_band_debug(mask: np.ndarray, zone_cols: dict, center_row_bands: list) -> np.ndarray:
    out = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    h = out.shape[0]
    for zone, (x1, x2) in zone_cols.items():
        color = (0, 255, 255) if zone == 'center' else (0, 200, 255)
        cv2.line(out, (x1, 0), (x1, h), color, 1)
        cv2.line(out, (x2, 0), (x2, h), color, 1)
    if 'center' in zone_cols:
        cx1, cx2 = zone_cols['center']
        for (y1, y2) in center_row_bands:
            cv2.line(out, (cx1, y1), (cx2, y1), (255, 0, 255), 1)
            cv2.line(out, (cx1, y2), (cx2, y2), (255, 0, 255), 1)
    return out


def main():
    bounds = find_window('Google Earth')
    img = screenshot_window(bounds)
    rois, dbg = detect_rois(img, debug=True)

    root = get_project_root()
    out_dir = os.path.join(root, 'data', 'screenshots')
    os.makedirs(out_dir, exist_ok=True)

    cv2.imwrite(os.path.join(out_dir, 'roi_debug.png'), draw_debug_boxes(img, rois))
    cv2.imwrite(os.path.join(out_dir, 'roi_mask.png'), dbg['mask'])
    cv2.imwrite(
        os.path.join(out_dir, 'roi_bands.png'),
        draw_band_debug(dbg['mask'], dbg['zone_cols'], dbg['center_row_bands'])
    )

    print(f"column bands: {dbg['col_bands']}")
    print(f"zone columns: {dbg['zone_cols']}")
    print(f"center row bands: {dbg['center_row_bands']}")

    out_path = os.path.join(root, 'config', 'rois.yaml')
    with open(out_path, 'w') as f:
        yaml.safe_dump(rois, f)
    print(f"rois saved to {out_path}")
    print(f"debug images: roi_debug.png, roi_mask.png, roi_bands.png in {out_dir}")


if __name__ == '__main__':
    main()