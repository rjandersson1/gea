"""
scripts/build_test_set_flight.py

Responsibilities:
  - Find GE window once (window should not move — no re-detection per frame)
  - Listen for single keypresses in the terminal:
      'p' -> wait 3s, then capture at 10 Hz for 10s into test_flight_10s/
      'o' -> stop
  - Numbers frames sequentially per run, does not overwrite existing files

Usage:
    python scripts/build_test_set_flight.py

Dependencies:
  - mss
  - opencv-python
  - numpy
  - src/utils/config.py
  - src/utils/timing.py         (RateLimiter)
  - scripts/calibrate_rois.py   (find_window, screenshot_window)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import tty
import termios

import cv2

from src.utils.config import get_project_root
from src.utils.timing import RateLimiter
from scripts.calibrate_rois import find_window, screenshot_window


CAPTURE_HZ = 10.0
CAPTURE_DURATION_S = 10.0
PRE_CAPTURE_DELAY_S = 3.0


def _read_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def _next_frame_index(out_dir: str) -> int:
    existing = [f for f in os.listdir(out_dir) if f.startswith('frame_') and f.endswith('.png')]
    if not existing:
        return 1
    indices = [int(f[len('frame_'):-len('.png')]) for f in existing]
    return max(indices) + 1


def run_burst(bounds: dict, out_dir: str) -> None:
    print(f"capturing in {PRE_CAPTURE_DELAY_S:.0f}s...")
    time.sleep(PRE_CAPTURE_DELAY_S)

    frame_idx = _next_frame_index(out_dir)
    n_frames = int(CAPTURE_HZ * CAPTURE_DURATION_S)

    limiter = RateLimiter(hz=CAPTURE_HZ)
    print(f"capturing {n_frames} frames at {CAPTURE_HZ} Hz...")

    for _ in range(n_frames):
        img = screenshot_window(bounds)
        path = os.path.join(out_dir, f'frame_{frame_idx:03d}.png')
        cv2.imwrite(path, img)
        frame_idx += 1
        limiter.sleep()

    print(f"burst complete: {n_frames} frames saved to {out_dir}")


def main():
    bounds = find_window('Google Earth')
    print(f"window locked: {bounds}")

    root = get_project_root()
    out_dir = os.path.join(root, 'data', 'screenshots', 'test_flight_10s')
    os.makedirs(out_dir, exist_ok=True)

    print("press 'p' to start a 10s capture burst (3s delay first), 'o' to stop")

    while True:
        key = _read_key()
        if key == 'p':
            run_burst(bounds, out_dir)
            print("\npress 'p' for another burst, 'o' to stop")
        elif key == 'o':
            print("stopped")
            break


if __name__ == '__main__':
    main()