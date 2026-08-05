"""
src/observation/ocr/types.py

Responsibilities:
  - Structured return type for all tape OCR parsers
  - Carries interpolated value plus the intermediate terms used to
    derive it, for debugging and downstream diagnostics

Dependencies:
  - dataclasses    (stdlib)
"""

from dataclasses import dataclass


@dataclass
class OCRReading:

    value: float | None = None
    anchor_token: str | None = None
    anchor_value: float | None = None
    offset_px: float | None = None
    offset_units: float | None = None
    clamped: bool = False
