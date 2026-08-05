"""
src/observation/ocr/types.py

Responsibilities:
  - Structured return type for all tape OCR parsers
  - Carries interpolated value plus the intermediate terms used to
    derive it, for debugging and downstream diagnostics

Dependencies:
  - dataclasses    (stdlib)
"""

from dataclasses import dataclass, field


@dataclass
class OCRReading:

    value: float | None = None
    anchor_token: str | None = None
    anchor_value: float | None = None
    offset_px: float | None = None
    offset_units: float | None = None
    clamped: bool = False


@dataclass
class LadderRung:

    value: float | None
    s: float
    centres: list = field(default_factory=list)
    n_labels: int = 0


@dataclass
class AttitudeReading:

    roll: float | None = None
    pitch: float | None = None
    pixels_per_unit: float | None = None
    fit_residual: float | None = None
    roll_ambiguous_180: bool = True
    n_segments: int = 0
    n_rungs: int = 0
    anchor_value: float | None = None
    rungs: list = field(default_factory=list)
