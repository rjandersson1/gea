"""
scripts/generate_labels_template.py

Responsibilities:
  - Scan data/screenshots/test_set/ for frames
  - Write a labels.csv template with frame names filled in,
    value columns blank for manual entry

Usage:
    python scripts/generate_labels_template.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv

from src.utils.config import get_project_root

FIELDS = ['heading_tape', 'airspeed_tape', 'altitude_tape']


def main():
    root = get_project_root()
    test_set_dir = os.path.join(root, 'data', 'screenshots', 'test_set')
    labels_path = os.path.join(test_set_dir, 'labels.csv')

    if os.path.exists(labels_path):
        print(f"{labels_path} already exists — not overwriting")
        return

    frames = sorted(f for f in os.listdir(test_set_dir) if f.endswith('.png'))

    with open(labels_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['frame'] + FIELDS)
        for frame in frames:
            writer.writerow([frame] + [''] * len(FIELDS))

    print(f"template written to {labels_path} — fill in {len(FIELDS)} columns for {len(frames)} frames")


if __name__ == '__main__':
    main()