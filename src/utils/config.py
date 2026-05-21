"""
utils/config.py

Responsibilities:
  - Load yaml config files and return as dicts
  - Resolve relative paths within config values
  - Single entry point for all config access across the project

Used by:
  - capture.py          (rois.yaml)
  - color_isolate.py    (ocr.yaml)
  - ocr/base.py         (ocr.yaml)
  - observation_manager.py
"""

import yaml
import os


def load_config(path: str) -> dict:
    """Load a yaml config file. path can be absolute or relative to project root."""
    pass


def get_project_root() -> str:
    """Return absolute path to project root (one level above src/)."""
    pass
