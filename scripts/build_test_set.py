"""
scripts/build_test_set.py

Responsibilities:
  - Find GE window once (window should not move — no re-detection per frame)
  - Listen for single keypresses in the terminal:
      'p' -> capture and save current window screenshot to test_set/
      'o' -> stop
  - Numbers frames sequentially, does not overwrite existing files on rerun

Usage:
    python scripts/build_test_set.py

Dependencies:
  - mss
  - opencv-python
  - numpy
  - src/utils/config.py
  - scripts/calibrate_rois.py   (find_window, screenshot_window)
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tty
import termios

import cv2

from src.utils.config import get_project_root
from scripts.calibrate_rois import find_window, screenshot_window


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


def main():
    bounds = find_window('Google Earth')
    print(f"window locked: {bounds}")

    root = get_project_root()
    out_dir = os.path.join(root, 'data', 'screenshots', 'test_set')
    os.makedirs(out_dir, exist_ok=True)

    frame_idx = _next_frame_index(out_dir)
    print("press 'p' to capture a frame, 'o' to stop")

    while True:
        key = _read_key()
        if key == 'p':
            img = screenshot_window(bounds)
            path = os.path.join(out_dir, f'frame_{frame_idx:03d}.png')
            cv2.imwrite(path, img)
            print(f"saved {path}")
            frame_idx += 1
        elif key == 'o':
            print("stopped")
            break


if __name__ == '__main__':
    main()