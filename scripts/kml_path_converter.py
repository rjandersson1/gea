"""
kml_path_converter.py

Converts a Google Earth Pro recorded tour (a gx:Tour KML produced by
Tools > Record a Tour, e.g. while flying in the Flight Simulator) into
a simple LineString path KML that can be reopened later to view the
route as a static line, instead of replaying the camera animation.

Extraction logic:
    - Each gx:FlyTo in the tour holds either a <Camera> (actual camera
      position - used once the Flight Simulator is active) or a
      <LookAt> (a ground point the camera is aimed at - used for the
      establishing zoom-in shot before the simulator starts).
    - If any <Camera> points exist, only those are used as the path,
      since they represent the recorded aircraft position. The
      <LookAt> intro points are skipped.
    - If no <Camera> points exist (a plain navigation tour), the
      <LookAt> points are used instead.

Altitude handling:
    - Recorded altitudes use gx:altitudeMode "relativeToSeaFloor" in
      Google Earth Pro. The output is written with altitudeMode
      "absolute", which is equivalent over land and a close
      approximation elsewhere.

Usage:
    Run this script directly. A file picker opens to select the
    recorded tour .kml. The converted path is saved next to the
    input file as "<name>_converted.kml".
"""

from __future__ import annotations

import os
import xml.etree.ElementTree as ET

NS = {
    "kml": "http://www.opengis.net/kml/2.2",
    "gx": "http://www.google.com/kml/ext/2.2",
}

Point = tuple[float, float, float]  # (longitude, latitude, altitude)


def select_file() -> str:
    """Open a file picker and return the chosen path, or exit if cancelled."""
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = askopenfilename(
        title="Select a Google Earth recorded tour (.kml)",
        filetypes=[("KML files", "*.kml"), ("All files", "*.*")],
    )
    root.destroy()
    if not path:
        raise SystemExit("No file selected.")
    return path


def _read_point(view_elem: ET.Element) -> Point | None:
    """Read longitude/latitude/altitude from a Camera or LookAt element."""
    lon = view_elem.find("kml:longitude", NS)
    lat = view_elem.find("kml:latitude", NS)
    alt = view_elem.find("kml:altitude", NS)

    if lon is None or lat is None or not lon.text or not lat.text:
        return None

    lon_v = float(lon.text)
    lat_v = float(lat.text)
    alt_v = float(alt.text) if alt is not None and alt.text else 0.0
    return (lon_v, lat_v, alt_v)


def extract_points(kml_path: str) -> tuple[list[Point], int]:
    """
    Extract the flown path from a recorded tour KML.

    Returns (points, skipped_lookat_count).
    """
    tree = ET.parse(kml_path)
    root = tree.getroot()

    flytos = root.findall(".//gx:Playlist/gx:FlyTo", NS)
    if not flytos:
        raise ValueError(
            "No gx:FlyTo elements found. This does not look like a "
            "recorded tour KML (Tools > Record a Tour output)."
        )

    camera_points: list[Point] = []
    lookat_points: list[Point] = []

    for flyto in flytos:
        cam = flyto.find("kml:Camera", NS)
        if cam is not None:
            point = _read_point(cam)
            if point:
                camera_points.append(point)
            continue

        look = flyto.find("kml:LookAt", NS)
        if look is not None:
            point = _read_point(look)
            if point:
                lookat_points.append(point)

    if camera_points:
        return camera_points, len(lookat_points)
    if lookat_points:
        return lookat_points, 0

    raise ValueError("No usable coordinates found in the tour.")


def correct_altitude_steps(
    points: list[Point], threshold_m: float = 200.0
) -> tuple[list[Point], list[tuple[int, float]]]:
    """
    Correct abrupt altitude step-discontinuities in a recorded path.

    Google Earth's tour recorder occasionally logs a bad camera pose for
    a single frame, producing a step in altitude that persists in
    subsequent points rather than reverting on the next sample (i.e. not
    a single-frame spike, but a level shift). This is treated as a
    recording artifact: any altitude change between consecutive points
    exceeding threshold_m is assumed spurious, and that offset is
    subtracted from every following point to restore a continuous curve.

    This is a heuristic correction, not a verified fix - it assumes any
    large jump is an artifact rather than a real, brief, sharp altitude
    change. Returns the corrected points and a log of (point_index,
    offset_removed_m) for each correction applied, so the corrections
    it made can be checked.

    Longitude/latitude are left untouched.
    """
    corrected: list[Point] = [points[0]]
    corrections: list[tuple[int, float]] = []
    cumulative_offset = 0.0

    for i in range(1, len(points)):
        lon, lat, alt = points[i]
        raw_delta = alt - points[i - 1][2]

        if abs(raw_delta) > threshold_m:
            cumulative_offset += raw_delta
            corrections.append((i, raw_delta))

        corrected.append((lon, lat, alt - cumulative_offset))

    return corrected, corrections


def build_path_kml(points: list[Point], doc_name: str) -> str:
    """Build a LineString path KML string from a list of points."""
    coords_str = " ".join(f"{lon},{lat},{alt}" for lon, lat, alt in points)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
\t<name>{doc_name}</name>
\t<Style id="s_recorded_path">
\t\t<LineStyle>
\t\t\t<color>ff0000ff</color>
\t\t\t<width>3</width>
\t\t</LineStyle>
\t</Style>
\t<Placemark>
\t\t<name>Recorded Path</name>
\t\t<styleUrl>#s_recorded_path</styleUrl>
\t\t<LineString>
\t\t\t<tessellate>1</tessellate>
\t\t\t<altitudeMode>absolute</altitudeMode>
\t\t\t<coordinates>
\t\t\t\t{coords_str}
\t\t\t</coordinates>
\t\t</LineString>
\t</Placemark>
</Document>
</kml>
"""


def convert(
    input_path: str, fix_altitude_steps: bool = False, step_threshold_m: float = 200.0
) -> tuple[str, int, int, list[tuple[int, float]]]:
    """
    Convert a recorded tour KML at input_path to a path KML.

    Returns (output_path, point_count, skipped_lookat_count, corrections).
    corrections is empty unless fix_altitude_steps is True.
    """
    points, skipped = extract_points(input_path)

    corrections: list[tuple[int, float]] = []
    if fix_altitude_steps:
        points, corrections = correct_altitude_steps(points, step_threshold_m)

    base, ext = os.path.splitext(input_path)
    suffix = "_converted_altfix" if fix_altitude_steps else "_converted"
    output_path = f"{base}{suffix}{ext or '.kml'}"

    kml_text = build_path_kml(points, os.path.basename(output_path))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kml_text)

    return output_path, len(points), skipped, corrections


if __name__ == "__main__":
    # Set to True to apply the altitude step-correction filter (see
    # correct_altitude_steps docstring - a heuristic, not a verified fix).
    FIX_ALTITUDE_STEPS = False

    selected_path = select_file()
    result_path, n_points, n_skipped, corrections = convert(
        selected_path, fix_altitude_steps=FIX_ALTITUDE_STEPS
    )

    print(f"Extracted {n_points} points.")
    if n_skipped:
        print(f"Skipped {n_skipped} intro LookAt points (used Camera positions instead).")
    if corrections:
        print(f"Corrected {len(corrections)} altitude step(s):")
        for idx, delta in corrections:
            print(f"  point {idx}: raw jump of {delta:+.1f} m removed")
    print(f"Saved: {result_path}")