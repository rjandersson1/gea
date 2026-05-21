"""
tests/observation/test_observation_manager.py

Tests for src/observation/observation_manager.py

Test cases:
  - step() returns dict with all Z_K_FIELDS keys
  - step() timestamp is a positive float
  - step() source dict contains expected source labels per field
  - None fields do not raise exceptions downstream
  - start/stop: KML poller lifecycle managed correctly
  - CSV logger: rows written to file after n steps

Note: full integration test requires GE running.
Unit tests mock ScreenCapture, parsers, KMLPoller individually.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.observation.observation_manager import ObservationManager, Z_K_FIELDS
