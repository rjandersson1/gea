"""
visualisation/plots/time_series.py

Responsibilities:
  - Generic rolling time series plotter for any set of scalar fields
  - Maintains a fixed time window (e.g. last 60 seconds)
  - update() appends new data point
  - show() renders live matplotlib figure (non-blocking)
  - save() writes figure to file
  - Base class for all phase-specific visualisers

Dependencies:
  - matplotlib
  - numpy
  - collections.deque   (stdlib, for rolling window)
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import deque


class TimeSeriesPlotter:

    def __init__(self, fields: list, window_s: float = 60.0, hz: float = 10.0):
        """
        Args:
            fields:    list of field name strings to plot
            window_s:  rolling window length in seconds
            hz:        expected update rate (used to size deque)
        """
        pass

    def update(self, data: dict) -> None:
        """
        Append one data point.

        Args:
            data: dict with 'timestamp' key and one key per field.
                  Missing or None values stored as np.nan.
        """
        pass

    def show(self) -> None:
        """Render/refresh live matplotlib figure. Non-blocking."""
        pass

    def save(self, path: str) -> None:
        """Save current figure to path."""
        pass

    def _init_figure(self) -> None:
        """Create figure and subplots (one subplot per field)."""
        pass

    def _redraw(self) -> None:
        """Update all subplot data from current deques."""
        pass
