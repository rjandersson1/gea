"""
observation/kml_poller.py

Responsibilities:
  - Watch the GoogleGeorge KML network link file for updates
  - Parse lat, lon, alt from KML on each update (~1 Hz)
  - Verify which fields GE actually writes (heading/airspeed TBC)
  - Run in a background thread; main loop calls get_latest()
  - Returns None if no new fix has arrived since last call

References:
  - KML mechanism described at:
    https://chrishills.org.uk/ChrisHills/GoogleGeorge/index.html
  - GE writes aircraft position to KML when NetworkLink is loaded
  - Requires GoogleGeorge.KML to be opened in GE (see README)

Dependencies:
  - xml.etree.ElementTree  (stdlib)
  - threading              (stdlib)
  - time                   (stdlib)
"""

import xml.etree.ElementTree as ET
import threading
import time


class KMLPoller:

    def __init__(self, kml_path: str, poll_interval: float = 1.0):
        """
        Args:
            kml_path:       path to the KML file GE writes to
            poll_interval:  seconds between file reads
        """
        pass

    def start(self) -> None:
        """Start background polling thread."""
        pass

    def stop(self) -> None:
        """Stop background thread."""
        pass

    def get_latest(self) -> dict | None:
        """
        Return most recent parsed fix, or None if no update since last call.

        Returns:
            dict with keys present in KML output, e.g.:
            {
                'lat':      float,
                'lon':      float,
                'alt':      float,
                'heading':  float|None,   # TBC — verify against real GE output
                'timestamp': float        # time.perf_counter() of last parse
            }
        """
        pass

    def _poll_loop(self) -> None:
        """Background thread: read file, parse, store."""
        pass

    def _parse_kml(self, kml_path: str) -> dict | None:
        """
        Parse KML file and extract aircraft state fields.
        Log which fields are present on first successful parse.
        """
        pass
