"""
src/observation/ocr/attitude.py

Responsibilities:
  - Estimate roll and pitch from the pitch-ladder ROI
  - Roll is derived from the orientation of the ladder rung lines
    themselves, by connected-component PCA. No OCR is involved
  - Pitch requires rung values, so it does use OCR: label positions
    come from connected components, values from a single sparse-text
    pass matched to those positions by bbox overlap
  - Pitch is fitted across all valued rungs (s = a + b * value) rather
    than read off a single anchor rung, which makes it continuous
    rather than quantised to the nearest labelled rung

Geometry:
  - u = unit vector along a rung, n = normal to it
  - s = projection of a point onto n, increasing down-screen
  - rung values increase up-screen, so b is negative and
    pixels_per_unit = -b, self-calibrated per frame

Known limits:
  - Roll is resolved modulo 180 degrees. roll_ambiguous_180 is always
    True; disambiguation needs external state (EKF)
  - Ladder labels stay screen-upright at all roll angles, so no
    deskew is applied before OCR

Dependencies:
  - numpy
  - opencv-python
  - tesserocr
  - Pillow
  - src/observation/ocr/base.py
  - src/observation/ocr/types.py
"""

import re
import numpy as np
import cv2
from PIL import Image
from tesserocr import RIL

from src.observation.ocr.base import BaseOCR
from src.observation.ocr.types import AttitudeReading, LadderRung


class AttitudeParser(BaseOCR):

    whitelist = '0123456789-'
    outlier_threshold = 90.0
    orientation = 'vertical'

    label_spacing_units = 5.0
    pixels_per_unit = None

    CLOSE_KERNEL = 5
    MIN_ELONGATION = 8.0
    MIN_SEG_LEN_MULT = 0.8
    ANGLE_TOL = 6.0
    CENTRE_EXCLUDE = 0.18
    RUNG_CLUSTER_MULT = 0.8
    PPU_MIN = 1.0
    PPU_MAX = 40.0

    GLYPH_H_MIN_MULT = 0.6
    GLYPH_H_MAX_MULT = 1.6
    GLYPH_AR_MAX = 1.3
    GLYPH_AREA_MULT = 0.15
    GROUP_DY_MULT = 0.5
    GROUP_GAP_MULT = 0.9

    VALID_CODES = {float(v) for v in range(-90, 95, 5)}

    def parse(self, img: np.ndarray) -> AttitudeReading:
        mask = self._preprocess(img)
        if mask is None or not mask.any():
            return AttitudeReading()

        h_ref = self._glyph_scale(mask)
        roll, n_segs = self._estimate_roll(mask, h_ref)
        if roll is None:
            return AttitudeReading()

        reading = AttitudeReading(roll=roll, n_segments=n_segs)

        labels = self._extract_labels(mask, h_ref)
        if not labels:
            return reading

        self._read_values(mask, labels)
        rungs = self._build_rungs(labels, roll)
        reading.rungs = rungs
        reading.n_rungs = len(rungs)

        H, W = mask.shape[:2]
        s_centre = self._project((W / 2.0, H / 2.0), roll)

        ppu = self._rung_spacing_ppu(labels, roll, h_ref)
        if ppu is None:
            return reading
        reading.pixels_per_unit = ppu

        anchor = self._pick_anchor(labels)
        if anchor is None:
            return reading

        s_anchor = self._project(anchor['centre'], roll)
        reading.anchor_value = anchor['value']
        reading.pitch = float(anchor['value'] + (s_anchor - s_centre) / ppu)
        return reading

    def _glyph_scale(self, mask: np.ndarray) -> float:
        n, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        if n < 2:
            return 12.0
        heights = np.array([stats[i, 3] for i in range(1, n)], dtype=float)
        tall = heights[heights >= np.percentile(heights, 75)]
        h_ref = float(np.median(tall)) if len(tall) else 12.0
        return h_ref if h_ref > 0 else 12.0

    def _estimate_roll(self, mask: np.ndarray, h_ref: float) -> tuple:
        closed = cv2.morphologyEx(
            mask, cv2.MORPH_CLOSE, np.ones((1, self.CLOSE_KERNEL), np.uint8)
        )
        n, lab, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
        if n < 2:
            return None, 0

        H, W = mask.shape[:2]
        cx, cy = W / 2.0, H / 2.0
        segments = []

        for i in range(1, n):
            x, y, w, h, _area = stats[i]
            if max(w, h) < self.MIN_SEG_LEN_MULT * h_ref:
                continue
            ys, xs = np.where(lab[y:y + h, x:x + w] == i)
            if len(xs) < 6:
                continue
            pts = np.stack([xs + x, ys + y], axis=1).astype(float)
            mu = pts.mean(axis=0)
            centred = pts - mu
            cov = (centred.T @ centred) / len(centred)
            evals, evecs = np.linalg.eigh(cov)
            elong = 1e9 if evals[0] < 1e-9 else evals[1] / evals[0]
            if elong < self.MIN_ELONGATION:
                continue
            if (abs(mu[0] - cx) < self.CENTRE_EXCLUDE * W
                    and abs(mu[1] - cy) < self.CENTRE_EXCLUDE * H):
                continue
            v = evecs[:, 1]
            angle = self._wrap180(np.degrees(np.arctan2(v[1], v[0])))
            weight = float(np.sqrt(evals[1]) * np.sqrt(len(pts)))
            segments.append((angle, weight))

        if not segments:
            return None, 0

        best = None
        for theta, _w in segments:
            inliers = [
                (a, w) for a, w in segments
                if abs(self._wrap180(a - theta)) <= self.ANGLE_TOL
            ]
            total = sum(w for _a, w in inliers)
            if best is None or total > best[0]:
                best = (total, inliers)

        inliers = best[1]
        return self._weighted_median(inliers), len(inliers)

    def _extract_labels(self, mask: np.ndarray, h_ref: float) -> list:
        n, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        glyphs = []
        for i in range(1, n):
            x, y, w, h, area = (int(v) for v in stats[i, :5])
            if not (self.GLYPH_H_MIN_MULT * h_ref <= h <= self.GLYPH_H_MAX_MULT * h_ref):
                continue
            if w > self.GLYPH_AR_MAX * h:
                continue
            if area < self.GLYPH_AREA_MULT * h_ref * h_ref:
                continue
            glyphs.append((x, y, w, h))

        glyphs.sort(key=lambda g: g[0])
        groups = []
        for g in glyphs:
            for grp in groups:
                gy = np.mean([b[1] + b[3] / 2 for b in grp])
                gx2 = max(b[0] + b[2] for b in grp)
                if (abs((g[1] + g[3] / 2) - gy) <= self.GROUP_DY_MULT * h_ref
                        and 0 <= (g[0] - gx2) <= self.GROUP_GAP_MULT * h_ref):
                    grp.append(g)
                    break
            else:
                groups.append([g])

        labels = []
        for grp in groups:
            x1 = min(b[0] for b in grp)
            y1 = min(b[1] for b in grp)
            x2 = max(b[0] + b[2] for b in grp)
            y2 = max(b[1] + b[3] for b in grp)
            labels.append({
                'bbox': (x1, y1, x2, y2),
                'centre': ((x1 + x2) / 2.0, (y1 + y2) / 2.0),
                'value': None,
                'token': None,
                'conf': None,
            })
        return labels

    def _read_values(self, mask: np.ndarray, labels: list) -> None:
        self._api.SetImage(Image.fromarray(mask))
        self._api.Recognize()
        ri = self._api.GetIterator()
        if ri is None:
            return

        tokens = []
        while True:
            try:
                text = (ri.GetUTF8Text(RIL.WORD) or '').strip()
                conf = ri.Confidence(RIL.WORD)
            except RuntimeError:
                text, conf = '', -1
            if text and conf >= 0:
                bbox = ri.BoundingBox(RIL.WORD)
                if bbox is not None:
                    tokens.append((text, bbox, conf))
            if not ri.Next(RIL.WORD):
                break

        for label in labels:
            lx1, ly1, lx2, ly2 = label['bbox']
            for text, (tx1, ty1, tx2, ty2), conf in tokens:
                if tx1 <= (lx1 + lx2) / 2 <= tx2 and ty1 <= (ly1 + ly2) / 2 <= ty2:
                    value = self._token_to_value(text)
                    if value is not None:
                        label['value'] = value
                        label['token'] = text
                        label['conf'] = conf
                    break

    def _build_rungs(self, labels: list, roll: float) -> list:
        by_value = {}
        for label in labels:
            if label['value'] is None:
                continue
            by_value.setdefault(label['value'], []).append(label)

        rungs = []
        for value, members in by_value.items():
            s = float(np.mean([self._project(m['centre'], roll) for m in members]))
            rungs.append(LadderRung(
                value=value,
                s=s,
                centres=[m['centre'] for m in members],
                n_labels=len(members),
            ))
        rungs.sort(key=lambda r: r.s)
        return rungs

    def _rung_spacing_ppu(self, labels: list, roll: float, h_ref: float):
        """
        Pixels-per-degree from the spacing of adjacent rungs. Uses only
        label geometry, not OCR values, so it stays valid on frames
        where the digits are misread.
        """
        if len(labels) < 3:
            return None
        s_vals = sorted(self._project(l['centre'], roll) for l in labels)

        clusters = [[s_vals[0]]]
        for s in s_vals[1:]:
            if s - clusters[-1][-1] <= self.RUNG_CLUSTER_MULT * h_ref:
                clusters[-1].append(s)
            else:
                clusters.append([s])
        centres = [float(np.mean(c)) for c in clusters]
        if len(centres) < 2:
            return None

        gaps = np.diff(centres)
        gaps = gaps[gaps > self.RUNG_CLUSTER_MULT * h_ref]
        if len(gaps) == 0:
            return None

        spacing = float(np.median(gaps))
        ppu = spacing / self.label_spacing_units
        if not (self.PPU_MIN <= ppu <= self.PPU_MAX):
            return None
        return ppu

    def _pick_anchor(self, labels: list):
        valued = [l for l in labels if l['value'] is not None]
        if not valued:
            return None
        return max(valued, key=lambda l: l['conf'] if l['conf'] is not None else -1)

    def _project(self, point: tuple, roll: float) -> float:
        theta = np.radians(roll)
        nx, ny = -np.sin(theta), np.cos(theta)
        return float(point[0] * nx + point[1] * ny)

    def _weighted_median(self, pairs: list) -> float:
        angles = np.array([a for a, _w in pairs], dtype=float)
        weights = np.array([w for _a, w in pairs], dtype=float)
        order = np.argsort(angles)
        angles, weights = angles[order], weights[order]
        cum = np.cumsum(weights)
        return float(angles[np.searchsorted(cum, cum[-1] / 2.0)])

    @staticmethod
    def _wrap180(angle: float) -> float:
        return (angle + 90.0) % 180.0 - 90.0

    def _token_to_value(self, token: str) -> float | None:
        """
        Accepts a lone label ('-10') or a token in which tesseract has
        merged both labels of one rung across the rung dashes
        ('30-30', '20---20'). Both labels of a rung carry the same
        value, so a merged token is unambiguous as long as its numeric
        runs agree. Sign is taken from a leading minus.
        """
        cleaned = token.strip()
        runs = re.findall(r'\d+', cleaned)
        if not runs:
            return None
        if len(set(runs)) != 1:
            return None

        value = float(runs[0])
        if cleaned.startswith('-'):
            value = -value
        return value if value in self.VALID_CODES else None
