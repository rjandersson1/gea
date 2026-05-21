"""
utils/timing.py

Responsibilities:
  - RateLimiter: block to maintain a fixed loop rate (e.g. 10 Hz)
  - LoopProfiler: record actual loop durations, report mean/p95/max
  - Used to ensure observation_manager.step() runs at target rate
    and to detect when OCR latency is blowing the loop budget

Used by:
  - observation_manager.py
  - scripts/run_goal_a.py
  - scripts/run_goal_b.py
"""

import time
import numpy as np


class RateLimiter:
    """Sleep to maintain a fixed loop rate."""

    def __init__(self, hz: float):
        """
        Args:
            hz: target loop frequency
        """
        pass

    def sleep(self) -> None:
        """Call at end of each loop iteration. Blocks until next cycle."""
        pass


class LoopProfiler:
    """Record loop durations and report statistics."""

    def __init__(self):
        pass

    def tick(self) -> None:
        """Call once per loop iteration."""
        pass

    def report(self) -> dict:
        """Return dict with keys: mean_ms, p95_ms, max_ms, n_samples."""
        pass
