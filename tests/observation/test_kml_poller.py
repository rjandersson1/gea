"""
tests/observation/test_kml_poller.py

Tests for src/observation/kml_poller.py

Test cases:
  - _parse_kml returns dict with lat, lon, alt for valid KML fixture
  - _parse_kml returns None for malformed XML
  - _parse_kml returns None for empty file
  - get_latest returns None before any fix arrives
  - get_latest returns dict after mock KML file is written
  - start/stop: background thread starts and stops cleanly
  - poll_interval respected: no more than 1 parse per interval

Fixtures:
  - tmp_kml_file: tmp_path with a valid minimal KML file
    (pytest tmp_path fixture)
"""

import pytest
import time
import os

from src.observation.kml_poller import KMLPoller


VALID_KML_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Placemark>
    <Point>
      <coordinates>-4.617434,56.146105,110</coordinates>
    </Point>
  </Placemark>
</kml>
"""
