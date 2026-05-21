"""
observation/observation_manager.py

Responsibilities:
  - Single entry point for all observation data
  - Initialises and owns: ScreenCapture, ColorIsolator, all OCR parsers,
    AttitudeEstimator, KMLPoller, CSVLogger
  - step() runs one full observation cycle and returns z_k dict
  - Timestamps every field at time of acquisition
  - Tracks source of each field (KML vs OCR vs CV) in z_k['source']
  - Attaches CSVLogger if log_path provided

z_k dict schema:
  {
    'timestamp':  float,         # time.perf_counter()
    'lat':        float|None,    # from KML
    'lon':        float|None,    # from KML
    'alt_kml':    float|None,    # from KML (MSL metres)
    'eye_alt':    float|None,    # from status bar OCR (MSL metres)
    'heading':    float|None,    # from heading tape OCR (degrees)
    'airspeed':   float|None,    # from airspeed tape OCR (knots)
    'altitude':   float|None,    # from altitude tape OCR (feet)
    'bank':       float|None,    # from attitude CV (degrees)
    'pitch':      float|None,    # from attitude CV (degrees)
    'source': {
        'lat': 'kml'|None,
        'heading': 'ocr'|None,
        'bank': 'cv'|None,
        ...
    }
  }

Dependencies:
  - src/observation/capture.py
  - src/observation/color_isolate.py
  - src/observation/ocr/heading.py
  - src/observation/ocr/airspeed.py
  - src/observation/ocr/altitude.py
  - src/observation/ocr/status_bar.py
  - src/observation/cv/attitude.py
  - src/observation/kml_poller.py
  - src/utils/config.py
  - src/utils/logger.py
"""

from src.observation.capture import ScreenCapture
from src.observation.color_isolate import ColorIsolator
from src.observation.ocr.heading import HeadingParser
from src.observation.ocr.airspeed import AirspeedParser
from src.observation.ocr.altitude import AltitudeParser
from src.observation.ocr.status_bar import StatusBarParser
from src.observation.cv.attitude import AttitudeEstimator
from src.observation.kml_poller import KMLPoller
from src.utils.config import load_config
from src.utils.logger import CSVLogger


Z_K_FIELDS = [
    'timestamp', 'lat', 'lon', 'alt_kml', 'eye_alt',
    'heading', 'airspeed', 'altitude', 'bank', 'pitch'
]


class ObservationManager:

    def __init__(
        self,
        rois_config_path: str,
        ocr_config_path: str,
        kml_path: str,
        log_path: str = None
    ):
        """
        Args:
            rois_config_path:  path to config/rois.yaml
            ocr_config_path:   path to config/ocr.yaml
            kml_path:          path to KML file watched by KMLPoller
            log_path:          optional CSV output path
        """
        pass

    def step(self) -> dict:
        """
        Run one observation cycle.

        Order of operations:
          1. grab full screenshot
          2. crop each ROI
          3. run OCR parsers on HUD ROIs
          4. run AttitudeEstimator on attitude ROI
          5. run StatusBarParser on status bar ROI
          6. get latest KML fix
          7. assemble z_k dict with timestamps and sources
          8. log to CSV if logger attached

        Returns:
            z_k dict (see module docstring for schema)
        """
        pass

    def start(self) -> None:
        """Start KML poller background thread."""
        pass

    def stop(self) -> None:
        """Stop KML poller and close CSV logger."""
        pass
