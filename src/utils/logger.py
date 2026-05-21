"""
utils/logger.py

Responsibilities:
  - Write z_k measurement dicts to CSV at each observation step
  - Handle None values gracefully (write empty string)
  - Flush periodically so data is not lost on crash
  - One logger instance shared across the pipeline via ObservationManager

Used by:
  - observation_manager.py
  - scripts/run_goal_a.py
  - scripts/run_goal_b.py
"""

import csv
import os
import time


class CSVLogger:
    """Append rows to a CSV file. Fields defined at init."""

    def __init__(self, path: str, fields: list):
        """
        Args:
            path:   output CSV file path
            fields: ordered list of column names
        """
        self.path = path
        self.fields = fields
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.file = open(path, 'w', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=fields)
        self.writer.writeheader()

    def log(self, row: dict) -> None:
        """Write a single row. Missing keys written as empty string."""
        row_with_defaults = {field: row.get(field, '') for field in self.fields}
        self.writer.writerow(row_with_defaults)
        self.file.flush()

    def close(self) -> None:
        """Flush and close the file handle."""
        self.file.close()
