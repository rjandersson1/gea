"""
tests/observation/benchmark_ocr.py

OCR accuracy and latency benchmark — not a unit test, run manually.

Usage:
    python -m tests.observation.benchmark_ocr

Responsibilities:
  - Run all OCR parsers against data/screenshots/test_set/
  - Compute per-field metrics: dropout_rate, outlier_rate, MAE, RMSE,
    p95_error, latency_mean_ms, latency_p95_ms
  - Sweep over ocr.yaml parameters (margin, dilation_radius,
    upscale_factor, threshold_method) and report Pareto front
    of accuracy vs latency
  - Output: printed table + saved CSV to data/logs/ocr_benchmark.csv
  - Use results to tune config/ocr.yaml

Dependencies:
  - numpy
  - pandas
  - src/observation/ocr/heading.py
  - src/observation/ocr/airspeed.py
  - src/observation/ocr/altitude.py
  - src/observation/color_isolate.py
  - src/utils/config.py
"""

import time
import numpy as np
import pandas as pd
from itertools import product

from src.observation.ocr.heading import HeadingParser
from src.observation.ocr.airspeed import AirspeedParser
from src.observation.ocr.altitude import AltitudeParser
from src.observation.color_isolate import ColorIsolator
from src.utils.config import load_config


PARAM_GRID = {
    'margin':           [20, 30, 40, 55, 70],
    'dilation_radius':  [0, 1, 2, 3],
    'upscale_factor':   [1, 2, 3],
    'threshold_method': ['otsu', 'adaptive'],
}


def run_benchmark(parser, images: list, ground_truth: list,
                  outlier_threshold: float) -> dict:
    """
    Run parser on all images, return metrics dict.

    Args:
        parser:             OCR parser instance with .parse() method
        images:             list of np.ndarray
        ground_truth:       list of float
        outlier_threshold:  abs error above which a result is an outlier

    Returns:
        dict with keys: n_total, dropout_rate, outlier_rate, mae, rmse,
                        p95_error, latency_mean_ms, latency_p95_ms
    """
    pass


def sweep_params(field: str, images: list, ground_truth: list) -> pd.DataFrame:
    """
    Run benchmark across PARAM_GRID for a single field.
    Returns DataFrame with one row per param combination.
    """
    pass


def main():
    """Load test set, run sweeps for all fields, print and save results."""
    pass


if __name__ == '__main__':
    main()
