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

        self.hz = hz
        self.period = 1.0 / hz
        self.next_time = time.time() + self.period
        pass

    def sleep(self) -> None:
        now = time.time()
        if self.next_time > now:
            time.sleep(self.next_time - now)
        self.next_time += self.period


class LoopProfiler:
    """Record loop durations and report statistics."""

    def __init__(self):
        self.durations = []

    def tick(self) -> None:
        """Call once per loop iteration."""
        self.durations.append(time.time())
        pass

    def report(self) -> dict:
        """Return dict with keys: mean_ms, p95_ms, max_ms, n_samples."""
        if not self.durations:
            return {'mean_ms': 0, 'p95_ms': 0, 'max_ms': 0, 'n_samples': 0}
        # Calculate durations (in seconds)
        if len(self.durations) < 2:
            return {'mean_ms': 0, 'p95_ms': 0, 'max_ms': 0, 'n_samples': len(self.durations)}
        durations = np.diff(self.durations)
        # Convert to milliseconds
        durations *= 1000
        return {
            'mean_ms': np.mean(durations),
            'p95_ms': np.percentile(durations, 95),
            'max_ms': np.max(durations),
            'n_samples': len(durations)
        }
