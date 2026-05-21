"""
visualisation/plots/measurement.py  —  Visualiser 1

Responsibilities:
  - Subclass of TimeSeriesPlotter preset for all z_k fields
  - Highlights dropout frames (None values) as red vertical bands
  - Overlays expected range bands per field (from ocr.yaml outlier thresholds)
  - Can be run live (fed from ObservationManager.step()) or
    replayed from a CSV log file

Usage (live):
    vis = MeasurementVisualiser()
    manager = ObservationManager(...)
    manager.start()
    while True:
        z_k = manager.step()
        vis.update(z_k)
        vis.show()

Usage (replay from CSV):
    vis = MeasurementVisualiser()
    vis.load_csv('data/logs/flight_001.csv')
    vis.show()

Dependencies:
  - src/visualisation/plots/time_series.py
  - src/observation/observation_manager.py    (Z_K_FIELDS)
  - matplotlib
  - numpy
  - pandas    (for CSV replay)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.visualisation.plots.time_series import TimeSeriesPlotter
from src.observation.observation_manager import Z_K_FIELDS


# expected plausible ranges per field for range band overlay
FIELD_RANGES = {
    'heading':  (0, 360),
    'airspeed': (0, 900),
    'altitude': (0, 60000),
    'bank':     (-90, 90),
    'pitch':    (-90, 90),
    'eye_alt':  (0, 20000),
}


class MeasurementVisualiser(TimeSeriesPlotter):

    def __init__(self, window_s: float = 60.0):
        """Preset with all z_k fields."""
        pass

    def load_csv(self, path: str) -> None:
        """
        Load a CSV log and replay all rows into the plotter.
        Use for offline analysis without GE running.
        """
        pass

    def _draw_dropout_bands(self, ax, field: str) -> None:
        """Shade regions where field value is NaN (dropout frames)."""
        pass

    def _draw_range_bands(self, ax, field: str) -> None:
        """Draw light shading for expected plausible range from FIELD_RANGES."""
        pass
