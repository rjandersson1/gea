"""
tests/observation/conftest.py

Shared pytest fixtures for observation tests.

Fixtures:
  - synthetic_heading_images:  list of (img, ground_truth) for heading
  - synthetic_airspeed_images: list of (img, ground_truth) for airspeed
  - synthetic_altitude_images: list of (img, ground_truth) for altitude
  - real_test_images:          list of (img, field, ground_truth) from
                               data/screenshots/test_set/labels.csv
  - default_isolator:          ColorIsolator with default config
  - default_ocr_config:        dict loaded from config/ocr.yaml

Synthetic images are generated at fixture setup time using PIL
(render known values in GE HUD font/color on black background).
Real images are loaded from data/screenshots/test_set/.
"""

import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os

from src.observation.color_isolate import ColorIsolator
from src.utils.config import load_config


@pytest.fixture(scope='session')
def default_isolator():
    pass


@pytest.fixture(scope='session')
def default_ocr_config():
    pass


@pytest.fixture(scope='session')
def synthetic_heading_images():
    """Generate (img, ground_truth) pairs for headings 0–355 step 5."""
    pass


@pytest.fixture(scope='session')
def synthetic_airspeed_images():
    """Generate (img, ground_truth) pairs for airspeeds 60–500 step 10."""
    pass


@pytest.fixture(scope='session')
def synthetic_altitude_images():
    """Generate (img, ground_truth) pairs for altitudes 0–50000 step 500."""
    pass


@pytest.fixture(scope='session')
def real_test_images():
    """
    Load annotated real screenshots from data/screenshots/test_set/.
    Reads labels.csv for ground truth.
    Returns list of dicts: {'img': np.ndarray, 'field': str, 'gt': float}
    """
    pass


def render_hud_value(value: str, size: tuple = (200, 60)) -> np.ndarray:
    """
    Render a string as green (#00FC00) text on black background.
    Approximates GE HUD font for synthetic test generation.
    """
    pass
