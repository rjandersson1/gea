# google-earth-autopilot

Autonomous flight controller for Google Earth Pro flight simulator.

## Project goals

- Goal A: high-speed HUD-based controller (F-16, LQR, 10 Hz OCR loop)
- Goal B: loiter/orbit controller (SR22, MPC, 1 Hz KML loop)

## Phase status

- [ ] Phase 1 — Observation pipeline
- [ ] Phase 2 — SysID
- [ ] Phase 3 — EKF
- [ ] Phase 4 — Inner loop controllers
- [ ] Phase 5 — MPC outer loop
- [ ] Phase 6 — ROS 2 wrapper
- [ ] Phase 7 — Display

## Setup

```bash
pip install -r requirements.txt
```

Tesseract binary required separately:
- macOS:  `brew install tesseract`
- Linux:  `apt install tesseract-ocr`
- Windows: https://github.com/UB-Mannheim/tesseract/wiki

## Phase 1 quickstart

1. Open Google Earth Pro, enter flight simulator (Ctrl+Alt+A)
2. Calibrate ROIs:
   ```bash
   python scripts/calibrate_rois.py
   ```
3. Run OCR benchmark on test set:
   ```bash
   python -m tests.observation.benchmark_ocr
   ```
4. Run unit tests:
   ```bash
   pytest tests/observation/
   ```

## KML setup (for Goal B)

Required for lat/lon position feedback.
See: https://chrishills.org.uk/ChrisHills/GoogleGeorge/index.html

Download GoogleGeorge.KML, open in GE, set kml_path in your run script.
