"""
observation/cv/hough.py

Responsibilities:
  - Wrapper around cv2.HoughLinesP for line detection
  - find_lines: general line detection on a binary/grayscale image
  - find_horizontal_lines: filter to lines within angle_tol of horizontal
  - line_angle: compute angle of a single line segment in degrees
  - Used by attitude.py to detect the pitch ladder zero-line

Dependencies:
  - numpy
  - opencv-python    (cv2)
"""

import numpy as np
import cv2
from dataclasses import dataclass


@dataclass
class Line:
    x1: int
    y1: int
    x2: int
    y2: int


def find_lines(
    img: np.ndarray,
    rho: float = 1,
    theta: float = None,     # defaults to np.pi/180
    threshold: int = 50,
    min_line_length: int = 20,
    max_line_gap: int = 10
) -> list:
    """
    Run HoughLinesP on img.

    Returns:
        List of Line objects
    """
    pass


def find_horizontal_lines(img: np.ndarray, angle_tol: float = 15.0) -> list:
    """
    Return lines within angle_tol degrees of horizontal.

    Args:
        img:        binary or grayscale image
        angle_tol:  max deviation from 0 degrees (horizontal)

    Returns:
        List of Line objects sorted by length descending
    """
    pass


def line_angle(line: Line) -> float:
    """
    Compute angle of line from horizontal in degrees.
    Positive = clockwise rotation.

    Returns:
        Angle in degrees, range [-90, 90]
    """
    pass


def line_length(line: Line) -> float:
    """Euclidean length of line segment."""
    pass
