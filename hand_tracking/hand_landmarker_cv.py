#!/usr/bin/env python3
"""
hand_landmarker_cv.py — 21 hand landmarks with NO MediaPipe, no model file.

Pure OpenCV + NumPy:

    skin mask  ->  largest blob  ->  palm centre & radius (distance transform)
               ->  fingertip peaks in a radial profile
               ->  21-point skeleton + gesture + robot-arm commands

Same landmark order, same JSON shape and the same arm protocol as
hand_landmarker.py, so anything consuming that output works unchanged.

READ THIS FIRST — what it is not
--------------------------------
This is geometry, not a neural network. There are no trained weights, which is
the point: no pip package beyond OpenCV/NumPy, no download, no MediaPipe, no
TensorFlow. The trade is accuracy:

  * It needs ONE hand, decent light, and a background that is not skin-coloured
    (a wall, a door, a sheet of paper — or run --calibrate to subtract the room).
  * No depth: z is always 0. Fingertips land on the real fingertips, but the
    knuckle joints are interpolated along each finger, so treat the skeleton as
    a readable pose -- not as a measurement.
  * Finger counting and open/closed/pinch are reliable at arm's length. Fine
    poses (OK sign, counting to three) are guesses — MediaPipe earns its keep
    there and this does not.
  * A face in frame is skin too: keep it out, or calibrate.

When to use which:
    hand_landmarker.py      accurate, 21 precise landmarks, needs mediapipe
    hand_landmarker_cv.py   no dependencies, coarse landmarks, needs a plain
                            background — good for an arm demo, gesture on/off,
                            base/elbow/pinch control

Quick start
-----------
    pip install opencv-python numpy      # that is the entire dependency list
    python hand_landmarker_cv.py                    # webcam
    python hand_landmarker_cv.py --calibrate        # same, but learn the room first
    python hand_landmarker_cv.py --image hand.jpg --out marked.jpg --json
    python hand_landmarker_cv.py --dry-run          # print arm commands

Keys: q quit · c calibrate · b box · k trail · g gestures · h hud · i indices ·
      space pause · s snapshot

MIT-style: do whatever you want with it.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Sequence, Tuple

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    sys.exit("OpenCV is missing. Run:  pip install opencv-python")

QUIET = False
VERSION = "1.0.0"


def log(*parts: object) -> None:
    if not QUIET:
        print(*parts, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

HAND_CONNECTIONS: Tuple[Tuple[int, int], ...] = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)

FINGER_NAMES = ("thumb", "index", "middle", "ring", "pinky")

# where each finger sits, as an angle away from the middle-finger axis
FINGER_ANGLES = {"thumb": 72.0, "index": 28.0, "middle": 0.0, "ring": -24.0, "pinky": -48.0}

C_BONE = (210, 210, 210)
C_JOINT = (255, 255, 255)
C_TIP = (80, 220, 255)
C_TEXT = (255, 255, 255)
C_ACCENT = (90, 230, 120)
C_DARK = (20, 20, 20)
C_BOX = (0, 200, 255)
C_MASK = (60, 220, 60)
FINGER_COLORS = {
    0: (60, 120, 240),
    1: (90, 220, 110),
    2: (250, 200, 60),
    3: (210, 90, 220),
    4: (70, 70, 250),
}
POINT_FINGER = (0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4)
POINT_IS_TIP = {4, 8, 12, 16, 20}


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass
class Hand:
    landmarks: np.ndarray                      # (21, 3) normalised, z = 0
    label: str                                 # "Left" / "Right" / "?"
    score: float                               # 0..1, a confidence proxy
    gesture: str = "NONE"
    pinch: float = 1.0
    fingers: Tuple[bool, ...] = (False,) * 5
    palm_center: Tuple[int, int] = (0, 0)
    palm_radius: float = 1.0
    tips: Tuple[int, ...] = ()                  # landmark indices that were really seen

    def px(self, index: int, width: int, height: int) -> Tuple[int, int]:
        x, y = self.landmarks[index][:2]
        return int(round(float(x) * width)), int(round(float(y) * height))

    def bbox(self, width: int, height: int, pad: int = 0) -> Tuple[int, int, int, int]:
        xs = self.landmarks[:, 0] * width
        ys = self.landmarks[:, 1] * height
        x1, y1 = int(xs.min()) - pad, int(ys.min()) - pad
        x2, y2 = int(xs.max()) + pad, int(ys.max()) + pad
        return (max(0, x1), max(0, y1), min(width - 1, x2), min(height - 1, y2))


# --------------------------------------------------------------------------- #
# Skin segmentation
# --------------------------------------------------------------------------- #

class HandSegmenter:
    """YCrCb skin threshold, optional static-background subtraction.

    YCrCb is the classic choice: chroma (Cr/Cb) barely moves with brightness,
    so the same two numbers work under a desk lamp and by a window. The
    background subtraction exists because skin thresholding on its own will
    happily grab a wooden door, a cardboard box or your face.
    """

    # Chroma box: Cr 133-173 / Cb 77-127. Widened slightly for darker skin
    # under warm indoor light.
    LOWER = np.array([0, 130, 74], dtype=np.uint8)
    UPPER = np.array([255, 180, 132], dtype=np.uint8)

    def __init__(self, min_area_fraction: float = 0.02, background_frames: int = 40) -> None:
        self.min_area_fraction = float(min_area_fraction)
        self.background_frames = int(background_frames)
        self.background: Optional[np.ndarray] = None
        self._samples: List[np.ndarray] = []
        self._calibrating = False

    # -- calibration -------------------------------------------------------- #
    @property
    def calibrating(self) -> bool:
        return self._calibrating

    def start_calibration(self) -> None:
        self._samples = []
        self._calibrating = True

    def feed_calibration(self, frame: np.ndarray) -> int:
        """Accumulate one empty-scene frame; returns how many are collected."""
        if not self._calibrating:
            return 0
        small = cv2.resize(frame, (160, int(160 * frame.shape[0] / frame.shape[1])))
        self._samples.append(small.astype(np.float32))
        if len(self._samples) > self.background_frames:
            self._samples.pop(0)
        if len(self._samples) >= self.background_frames:
            self.background = np.median(np.stack(self._samples), axis=0).astype(np.uint8)
            self._calibrating = False
            self._samples = []
            log("[cv] background calibrated — keep the camera still from here on")
        return len(self._samples)

    def clear_background(self) -> None:
        self.background = None
        self._samples = []
        self._calibrating = False

    # -- mask --------------------------------------------------------------- #
    def mask(self, frame: np.ndarray) -> np.ndarray:
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        ycrcb = cv2.cvtColor(blurred, cv2.COLOR_BGR2YCrCb)
        skin = cv2.inRange(ycrcb, self.LOWER, self.UPPER)

        if self.background is not None:
            small = cv2.resize(frame, (self.background.shape[1], self.background.shape[0]))
            diff = cv2.absdiff(small, self.background).max(axis=2)
            moved = (diff > 18).astype(np.uint8) * 255
            moved = cv2.resize(moved, (frame.shape[1], frame.shape[0]),
                               interpolation=cv2.INTER_NEAREST)
            moved = cv2.dilate(moved, np.ones((9, 9), np.uint8))
            skin = cv2.bitwise_and(skin, moved)

        kernel = np.ones((5, 5), np.uint8)
        skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, kernel)
        skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Nails, specular highlights, rings and printed logos leave holes
        # *inside* the hand. Every ray cast from the palm centre would stop at
        # the first hole, so fill all enclosed regions: a hole in the middle of
        # a silhouette is never background.
        contours, _ = cv2.findContours(skin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(skin)
        cv2.drawContours(filled, contours, -1, 255, thickness=-1)
        return filled


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #

def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else np.zeros_like(v)


def _angle_deg(v: np.ndarray) -> float:
    return math.degrees(math.atan2(float(v[1]), float(v[0])))


def _wrap(deg: float) -> float:
    return (deg + 180.0) % 360.0 - 180.0


def _polar(c: np.ndarray, deg: float, r: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([c[0] + r * math.cos(a), c[1] + r * math.sin(a)], dtype=np.float32)


def radial_profile(mask: np.ndarray, center: Tuple[float, float],
                   step_deg: float = 1.0, max_r: Optional[float] = None) -> np.ndarray:
    """Distance from `center` to the mask edge, sampled around the circle.

    The palm centre is inside the blob, so the mask is contiguous outward from
    it: the profile is the number of inside samples along each ray.
    """
    h, w = mask.shape[:2]
    if max_r is None:
        max_r = float(np.hypot(max(center[0], w - center[0]), max(center[1], h - center[1])))
    n_angles = int(360 / step_deg)
    n_r = max(8, int(max_r))
    angles = np.deg2rad(np.arange(n_angles) * step_deg)
    radii = np.arange(1, n_r + 1, dtype=np.float32)

    xs = center[0] + np.cos(angles)[:, None] * radii[None, :]
    ys = center[1] + np.sin(angles)[:, None] * radii[None, :]
    xi = np.clip(xs.astype(np.int32), 0, w - 1)
    yi = np.clip(ys.astype(np.int32), 0, h - 1)
    inside = mask[yi, xi] > 0

    # run length of consecutive inside samples starting at radius 1
    valid = np.cumprod(inside, axis=1)
    profile = valid.sum(axis=1).astype(np.float32)
    return profile


def palm_circle(mask: np.ndarray) -> Tuple[np.ndarray, float, Optional[np.ndarray]]:
    """Find the palm: the wide, blobby part of the hand, not the forearm.

    The naive "biggest circle inside the mask" lands in the forearm, which is
    usually thicker than the palm and runs off the edge of the frame. So:
    find every local maximum of the distance transform, work out which end of
    the blob is the free end (farthest from the frame border it enters by), and
    take the wide peak nearest that end. Returns (centre, radius, arm_dir)
    where arm_dir points from the palm back toward the forearm, or None.
    """
    h, w = mask.shape[:2]
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    if float(dist.max()) < 6:
        return np.array([w / 2.0, h / 2.0], np.float32), 0.0, None

    # local maxima of the distance transform
    win = max(15, int(round(min(h, w) * 0.06)) | 1)
    peaks = (dist >= cv2.dilate(dist, np.ones((win, win), np.uint8)) - 0.5) & (dist > 8)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        peaks.astype(np.uint8), connectivity=8)
    candidates = []
    for i in range(1, count):
        cx, cy = centroids[i]
        r = float(dist[int(cy), int(cx)])
        if r <= 0:
            r = float(dist[labels == i].max())
        candidates.append((r, np.array([cx, cy], np.float32)))
    if not candidates:
        _, _, _, loc = cv2.minMaxLoc(dist)
        return np.array(loc, np.float32), float(dist[loc]), None

    # where does the blob touch the frame? that is the forearm side
    band = max(2, int(round(min(h, w) * 0.01)))
    border = np.zeros_like(mask)
    border[:band, :] = mask[:band, :]
    border[-band:, :] = mask[-band:, :]
    border[:, :band] = mask[:, :band]
    border[:, -band:] = mask[:, -band:]
    arm_dir = None
    if border.any():
        ys, xs = np.nonzero(border)
        contact = np.array([xs.mean(), ys.mean()], np.float32)
    else:
        ys, xs = np.nonzero(mask)
        contact = np.array([xs.mean(), ys.mean()], np.float32)

    ys, xs = np.nonzero(mask)
    far = np.argmax((xs - contact[0]) ** 2 + (ys - contact[1]) ** 2)
    free_end = np.array([xs[far], ys[far]], np.float32)

    # The palm is the widest part of the blob *between* the forearm and the
    # fingers. So: keep the wide peaks (narrow ones are fingers) and take the
    # one projected farthest from where the arm enters the frame.
    best_r = max(r for r, _ in candidates)
    wide = [(r, c) for r, c in candidates if r >= 0.55 * best_r]
    reach = _unit(free_end - contact)
    radius, center = max(wide, key=lambda rc: float(np.dot(rc[1] - contact, reach)))

    delta = np.array([contact[0] - center[0], contact[1] - center[1]], np.float32)
    if np.linalg.norm(delta) > radius:
        arm_dir = _unit(delta)
    return center, radius, arm_dir


def find_peaks(profile: np.ndarray, min_value: float, prominence: float,
               min_separation_deg: float, step_deg: float) -> List[int]:
    """Indices of local maxima in a circular profile."""
    n = len(profile)
    span = max(1, int(round(min_separation_deg / step_deg)))
    # No smoothing: a thumb held against a wide palm shows up as a sharp step
    # in the profile, and averaging across it erases the step entirely.
    smooth = profile
    candidates = []
    for i in range(n):
        window_vals = [smooth[(i + d) % n] for d in range(-span, span + 1)]
        if smooth[i] < max(window_vals):
            continue
        if smooth[i] < min_value:
            continue
        left = min(smooth[(i - d) % n] for d in range(1, span + 1))
        right = min(smooth[(i + d) % n] for d in range(1, span + 1))
        if smooth[i] - max(left, right) < prominence:
            continue
        candidates.append(i)

    # keep the strongest peak in each cluster
    kept: List[int] = []
    for i in sorted(candidates, key=lambda k: -smooth[k]):
        if all(min(abs(i - k), n - abs(i - k)) > span for k in kept):
            kept.append(i)
    return sorted(kept)


# --------------------------------------------------------------------------- #
# The detector
# --------------------------------------------------------------------------- #

class CVHandDetector:
    """Skin blob -> palm circle -> fingertips -> 21 landmarks."""

    def __init__(self, segmenter: Optional[HandSegmenter] = None,
                 min_area_fraction: float = 0.02,
                 smooth: float = 0.4) -> None:
        self.segmenter = segmenter or HandSegmenter(min_area_fraction)
        self.min_area_fraction = float(min_area_fraction)
        self.smooth = max(0.0, min(1.0, float(smooth)))
        self._prev: Optional[np.ndarray] = None

    # -- public ------------------------------------------------------------- #
    def detect(self, frame: np.ndarray, mirror: bool = True) -> List[Hand]:
        h, w = frame.shape[:2]
        mask = self.segmenter.mask(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            self._prev = None
            return []

        contour = max(contours, key=cv2.contourArea)
        if cv2.contourArea(contour) < self.min_area_fraction * h * w:
            self._prev = None
            return []

        hand = self._build(contour, mask, w, h, mirror)
        if hand is None:
            self._prev = None
            return []
        return [hand]

    def reset(self) -> None:
        self._prev = None

    # -- internals ---------------------------------------------------------- #
    def _build(self, contour: np.ndarray, mask: np.ndarray, w: int, h: int,
               mirror: bool) -> Optional[Hand]:
        center, radius, arm_dir = palm_circle(mask)
        if radius < 8:
            return None

        profile = radial_profile(mask, center, step_deg=2.0)
        step_deg = 2.0
        n = len(profile)

        # The forearm is a wide, smooth, very long run in the profile. Ignore
        # that whole sector so it cannot masquerade as a fat thumb.
        arm_span = None
        if arm_dir is not None:
            arm_idx = int(round((math.degrees(math.atan2(float(arm_dir[1]), float(arm_dir[0])))
                                 % 360.0) / step_deg))
            half = int(round(34.0 / step_deg))
            arm_span = (arm_idx - half, arm_idx + half)
        else:
            arm_idx = int(np.argmax(profile))
            arm_width = 0
            for d in range(0, n // 2):
                if profile[(arm_idx + d) % n] > 2.2 * radius:
                    arm_width = d
                else:
                    break
            if arm_width > 0:
                arm_span = (arm_idx - arm_width, arm_idx + arm_width)

        peaks = find_peaks(profile, min_value=1.25 * radius, prominence=0.18 * radius,
                           min_separation_deg=9.0, step_deg=step_deg)
        if arm_span is not None:
            lo, hi = arm_span
            peaks = [p for p in peaks if not (0 <= (p - lo) % n <= (hi - lo) % n)]
        peaks = [p for p in peaks if profile[p] < 4.2 * radius]      # not the arm again

        # A closed fist still has a bumpy silhouette (four knuckles), and those
        # bumps can clear the peak threshold. The giveaway is that a fist is
        # convex: the deepest notch between adjacent protrusions is shallow.
        # Spread fingers cut deep V's into the outline, so measure that.
        depth = 0.0
        try:
            hull = cv2.convexHull(contour, returnPoints=False)
            if hull is not None and len(hull) >= 3:
                defects = cv2.convexityDefects(contour, hull)
                if defects is not None:
                    depth = float(np.asarray(defects).reshape(-1, 4)[:, 3].max()) / 256.0
        except Exception:
            depth = float("inf")        # cannot tell -> do not call it a fist
        closed_hand = depth < 0.95 * radius
        if closed_hand:
            peaks = []

        # A ray from the palm centre often clips the *side* of a splayed finger
        # instead of its tip, so the profile run-length under-reads. Snap each
        # peak direction to the farthest contour point inside a narrow window
        # around it -- on a real fingertip that is the tip itself.
        cpts = contour.reshape(-1, 2).astype(np.float32) - center
        cang = np.degrees(np.arctan2(cpts[:, 1], cpts[:, 0])) % 360.0
        cr = np.hypot(cpts[:, 0], cpts[:, 1])

        tip_points: List[Tuple[float, np.ndarray, float]] = []
        for p in peaks:
            deg = p * step_deg
            d = np.abs((cang - deg + 180.0) % 360.0 - 180.0)
            sel = d <= 9.0
            if sel.any():
                j = int(np.argmax(np.where(sel, cr, -1.0)))
                tip_points.append((deg, center + cpts[j], float(cr[j])))
            else:
                r = float(profile[p])
                tip_points.append((deg, _polar(center, deg, r), r))

        # Palm axis: the mean direction of the fingertips, but the thumb is a
        # long way off-axis and would drag the mean toward itself, so drop the
        # most extreme tip and re-average the rest.
        def _mean_axis(angles_deg):
            v = np.zeros(2, dtype=np.float64)
            for a in angles_deg:
                r_ = math.radians(a)
                v += (math.cos(r_), math.sin(r_))
            v = _unit(v.astype(np.float32))
            if float(np.linalg.norm(v)) < 1e-6:
                v = np.array([0.0, -1.0], dtype=np.float32)
            return _angle_deg(v)

        if len(tip_points) >= 3:
            degs = [d for d, _, _ in tip_points]
            rough = _mean_axis(degs)
            spread_i = int(np.argmax([abs(_wrap(d - rough)) for d in degs]))
            inner = [d for i, d in enumerate(degs) if i != spread_i]
            axis_deg = _mean_axis(inner)
        else:
            # One or two tips is not enough to average a direction; fingers
            # point away from the forearm, so use that instead.
            if arm_dir is not None:
                axis_deg = _angle_deg(-arm_dir)
            elif tip_points:
                axis_deg = _angle_deg(tip_points[0][1] - center)
            else:
                fallback = _unit(np.array([center[0] - w / 2.0, center[1] - h / 2.0],
                                          dtype=np.float32))
                if float(np.linalg.norm(fallback)) < 1e-6:
                    fallback = np.array([0.0, -1.0], dtype=np.float32)
                axis_deg = _angle_deg(fallback)

        # fingertip angles relative to the palm axis
        rel = [(_wrap(deg - axis_deg), tip, r) for deg, tip, r in tip_points]

        # ---- which fingertip belongs to which finger? ---------------------- #
        # Fingertip peaks always come in anatomical order along the fan, so
        # treat it as a sequence alignment: match the sorted peaks to the five
        # slots in order, allowing a slot or a peak to be skipped (a finger
        # that is curled away simply produced no peak). Both thumb sides are
        # tried and the cheaper explanation wins.
        finger_slots = ("thumb", "index", "middle", "ring", "pinky")
        SKIP = 25.0        # degrees; skipping is cheaper than a bad match

        def _ordered(sign: float):
            return sorted(finger_slots, key=lambda n: _wrap(sign * FINGER_ANGLES[n]))

        def _align(sign: float):
            order = _ordered(sign)
            want = [_wrap(sign * FINGER_ANGLES[n]) for n in order]
            peaks_sorted = sorted(range(len(rel)), key=lambda j: rel[j][0])
            vals = [rel[j][0] for j in peaks_sorted]
            nS, nP = len(want), len(vals)
            inf = float("inf")
            cost = [[inf] * (nP + 1) for _ in range(nS + 1)]
            back = [[None] * (nP + 1) for _ in range(nS + 1)]
            cost[0][0] = 0.0
            for i in range(nS + 1):
                for j in range(nP + 1):
                    if cost[i][j] == inf:
                        continue
                    if i < nS and j < nP:
                        c = cost[i][j] + abs(_wrap(vals[j] - want[i]))
                        if c < cost[i + 1][j + 1]:
                            cost[i + 1][j + 1] = c
                            back[i + 1][j + 1] = (i, j, True)
                    if i < nS and cost[i][j] + SKIP < cost[i + 1][j]:
                        cost[i + 1][j] = cost[i][j] + SKIP
                        back[i + 1][j] = (i, j, False)
                    if j < nP and cost[i][j] + SKIP < cost[i][j + 1]:
                        cost[i][j + 1] = cost[i][j] + SKIP
                        back[i][j + 1] = (i, j, False)
            got: Dict[str, Tuple[np.ndarray, float]] = {}
            i, j = nS, nP
            while i > 0 or j > 0:
                pi, pj, matched_here = back[i][j]
                if matched_here:
                    name = order[pi]
                    tip, r = rel[peaks_sorted[pj]][1], rel[peaks_sorted[pj]][2]
                    got[name] = (tip, r)
                i, j = pi, pj
            return got, cost[nS][nP]

        best = None
        for sign in (1.0, -1.0):
            got, total = _align(sign)
            key = (len(got), -total)
            if best is None or key > best[0]:
                best = (key, sign, got)
        _, thumb_sign, matched = best
        detected: List[Tuple[str, np.ndarray, float]] = [
            (name, tip, r) for name, (tip, r) in matched.items()]

        def slot_angle(name: str) -> float:
            return axis_deg + thumb_sign * FINGER_ANGLES[name]

        # ---- build the 21 landmarks in MediaPipe's canonical order --------- #
        pts = np.zeros((21, 3), dtype=np.float32)
        if arm_dir is not None:
            wrist = center + arm_dir * (1.7 * radius)
        else:
            wrist = _polar(center, axis_deg + 180.0, 1.7 * radius)
        pts[0, :2] = [np.clip(wrist[0], 0, w - 1), np.clip(wrist[1], 0, h - 1)]

        seen_tips: List[int] = []
        finger_flags: List[bool] = []
        for slot, name in enumerate(finger_slots):
            base_i = 1 if name == "thumb" else 5 + 4 * (slot - 1)
            match = next((d for d in detected if d[0] == name), None)

            if match is not None:
                _, tip, r = match
                mcp_r = 1.00 * radius if name != "thumb" else 0.85 * radius
                mcp = _polar(center, slot_angle(name), mcp_r)
                for k, idx in enumerate(range(base_i, base_i + 4)):
                    frac = (0.30, 0.55, 0.78, 1.0)[k]
                    pts[idx, :2] = mcp + (tip - mcp) * frac
                seen_tips.append(base_i + 3)
                finger_flags.append(r > 1.55 * radius)
            else:
                # curled / hidden: a short chain folded back toward the palm
                mcp = _polar(center, slot_angle(name), 0.95 * radius)
                curls = (1.02, 0.92, 0.86)
                for k, idx in enumerate(range(base_i, base_i + 4)):
                    if k == 0:
                        pts[idx, :2] = mcp
                    else:
                        pts[idx, :2] = _polar(center, slot_angle(name), radius * curls[k - 1])
                finger_flags.append(False)

        # ---- gesture ------------------------------------------------------- #
        thumb_ok = next((d for d in detected if d[0] == "thumb"), None) is not None
        index_ok = next((d for d in detected if d[0] == "index"), None) is not None
        ext = sum(1 for i, f in enumerate(finger_flags) if f and i > 0)
        pinch = 1.0
        if thumb_ok and index_ok:
            pinch = float(np.linalg.norm(pts[4, :2] - pts[8, :2]) / max(radius, 1e-3))

        thumb_vec = pts[4, :2] - pts[2, :2]
        if ext == 0 and not finger_flags[0]:
            gesture = "FIST"
        elif (thumb_ok and index_ok and pinch < 0.62
              and np.linalg.norm(pts[8, :2] - pts[5, :2]) > 1.0 * radius):
            gesture = "PINCH"
        elif ext >= 4:
            gesture = "OPEN_PALM" if finger_flags[0] else "FOUR"
        elif ext == 3:
            gesture = "THREE"
        elif ext == 2:
            gesture = "PEACE"
        elif ext == 1:
            gesture = "POINT"
        elif finger_flags[0]:
            gesture = "THUMBS_UP" if thumb_vec[1] < -0.35 * radius else (
                "THUMBS_DOWN" if thumb_vec[1] > 0.35 * radius else "FIST")
        else:
            gesture = "NONE"

        # ---- handedness ---------------------------------------------------- #
        # Pure 2D geometry, calibrated on a labelled right-hand photo: with the
        # thumb on the low-angle side of the palm axis it is a right hand. It
        # survives rotation, but it is a guess -- --no-mirror flips it. With
        # fewer than two fingertips there is nothing to read chirality from
        # (a fist is a blob), so say so instead of guessing.
        if len(matched) >= 2:
            side = thumb_sign if mirror else -thumb_sign
            label = "Right" if side > 0 else "Left"
        else:
            label = "?"

        # ---- smooth and normalise ------------------------------------------ #
        pts[:, 2] = 0.0
        if self._prev is not None and self._prev.shape == pts.shape and self.smooth > 0:
            a = self.smooth
            pts = a * pts + (1.0 - a) * self._prev
        self._prev = pts.copy()

        norm = pts.copy()
        norm[:, 0] /= w
        norm[:, 1] /= h

        quality = min(1.0, 0.35 + 0.1 * len(detected) + (0.15 if radius > 20 else 0.0))
        return Hand(
            landmarks=norm,
            label=label,
            score=float(quality),
            gesture=gesture,
            pinch=float(pinch),
            fingers=tuple(finger_flags),
            palm_center=(int(center[0]), int(center[1])),
            palm_radius=float(radius),
            tips=tuple(seen_tips),
        )


# --------------------------------------------------------------------------- #
# Drawing
# --------------------------------------------------------------------------- #

def _line_thickness(height: int) -> int:
    return max(1, int(round(height / 320)))


def _text(frame: np.ndarray, text: str, org: Tuple[int, int], scale: float,
          color: Tuple[int, int, int] = C_TEXT, thick: int = 1) -> None:
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, C_DARK,
                thick + 2, cv2.LINE_AA)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                thick, cv2.LINE_AA)


def draw_hand(frame: np.ndarray, hand: Hand, *, show_labels: bool = True,
              show_indices: bool = False, show_bbox: bool = False,
              show_seen: bool = False) -> None:
    h, w = frame.shape[:2]
    thick = _line_thickness(h)
    r = max(2, int(round(min(w, h) * 0.007)))

    if show_bbox:
        x1, y1, x2, y2 = hand.bbox(w, h, pad=int(min(w, h) * 0.03))
        cv2.rectangle(frame, (x1, y1), (x2, y2), C_DARK, thick + 3, cv2.LINE_AA)
        cv2.rectangle(frame, (x1, y1), (x2, y2), C_BOX, thick + 1, cv2.LINE_AA)

    if show_seen:
        cv2.circle(frame, hand.palm_center, int(hand.palm_radius), (90, 90, 90), 1, cv2.LINE_AA)

    for a, b in HAND_CONNECTIONS:
        color = FINGER_COLORS[POINT_FINGER[b]] if b not in (0, 5, 9, 13, 17) else C_BONE
        dim = show_seen and b not in hand.tips and b not in (0,)
        cv2.line(frame, hand.px(a, w, h), hand.px(b, w, h),
                 (90, 90, 90) if dim else color, thick, cv2.LINE_AA)

    for i in range(21):
        x, y = hand.px(i, w, h)
        seen = (not show_seen) or i in hand.tips or i == 0
        color = C_TIP if (i in POINT_IS_TIP and seen) else C_JOINT
        if not seen:
            color = (110, 110, 110)
        cv2.circle(frame, (x, y), r, C_DARK, -1, cv2.LINE_AA)
        cv2.circle(frame, (x, y), max(1, r - max(1, thick // 2)), color, -1, cv2.LINE_AA)

    if show_indices:
        scale = 0.35 * max(0.8, min(w, h) / 720)
        for i in range(21):
            x, y = hand.px(i, w, h)
            cv2.putText(frame, str(i), (x + r + 2, y - r), cv2.FONT_HERSHEY_SIMPLEX,
                        scale, C_DARK, 2, cv2.LINE_AA)
            cv2.putText(frame, str(i), (x + r + 2, y - r), cv2.FONT_HERSHEY_SIMPLEX,
                        scale, C_TEXT, 1, cv2.LINE_AA)

    if show_labels:
        x, y = hand.px(0, w, h)
        text = f"{hand.label} {hand.score:.2f}" if hand.label != "?" else f"{hand.score:.2f}"
        _text(frame, text, (x + int(min(w, h) * 0.03), y + int(min(w, h) * 0.05)),
              max(0.45, min(w, h) / 900), C_ACCENT, 2)


def draw_mask(frame: np.ndarray, mask: np.ndarray) -> None:
    """Inset of the skin mask — the tuning view."""
    h, w = frame.shape[:2]
    small = cv2.resize(mask, (w // 4, h // 4), interpolation=cv2.INTER_NEAREST)
    color = cv2.cvtColor(small, cv2.COLOR_GRAY2BGR)
    color[:, :, 1] = np.maximum(color[:, :, 1], small)
    x0, y0 = w - small.shape[1] - 10, h - small.shape[0] - 10
    frame[y0:y0 + small.shape[0], x0:x0 + small.shape[1]] = color


def draw_hud(frame: np.ndarray, lines: Sequence[str], *, show_help: bool = False) -> None:
    h, w = frame.shape[:2]
    if not lines:
        return
    scale = max(0.38, min(0.75, min(w, h) / 900))
    pad = int(10 * scale / 0.6)
    line_h = int(24 * scale / 0.6)
    width = max(cv2.getTextSize(t, cv2.FONT_HERSHEY_SIMPLEX, scale, 1)[0][0] for t in lines) + 2 * pad
    height = line_h * len(lines) + 2 * pad

    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (10 + width, 10 + height), C_DARK, -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    for i, text in enumerate(lines):
        y = 10 + pad + line_h * (i + 1) - int(line_h * 0.3)
        cv2.putText(frame, text, (10 + pad, y), cv2.FONT_HERSHEY_SIMPLEX, scale,
                    C_ACCENT if i == 0 else C_TEXT, 1, cv2.LINE_AA)

    if show_help:
        help_lines = ["q quit   s snapshot   c calibrate   m mirror   b box",
                      "k trail   g gestures   h hud   i indices   space pause"]
        y0 = h - pad - line_h * (len(help_lines) - 1) - pad
        for j, text in enumerate(help_lines):
            cv2.putText(frame, text, (10 + pad, y0 + j * line_h), cv2.FONT_HERSHEY_SIMPLEX,
                        scale * 0.8, C_TEXT, 1, cv2.LINE_AA)


def draw_trail(frame: np.ndarray, points: Sequence[Tuple[int, int]]) -> None:
    thick = max(2, _line_thickness(frame.shape[0]) + 1)
    n = len(points)
    for i in range(1, n):
        fade = i / n
        cv2.line(frame, points[i - 1], points[i],
                 (int(90 * fade), int(200 * fade), int(255 * fade)), thick, cv2.LINE_AA)


# --------------------------------------------------------------------------- #
# Robot-arm bridge — identical protocol to hand_landmarker.py
# --------------------------------------------------------------------------- #

class ArmController:
    BASE_RANGE = (0, 300)
    ELBOW_RANGE = (30, 150)
    HEAD_RANGE = (45, 135)
    LIGHT_GESTURES = {"THUMBS_UP": "TW#", "THUMBS_DOWN": "TC#", "PEACE": "TN#"}

    def __init__(self, port: Optional[str] = None, baud: int = 9600,
                 dry_run: bool = False, hz: float = 12.0, mirror: bool = True,
                 deadband: int = 2) -> None:
        self.dry_run = dry_run or not port
        self.deadband = max(0, int(deadband))
        self.period = 1.0 / max(1.0, float(hz))
        self.mirror = mirror
        self._ser = None
        self._last_send = 0.0
        self._last: dict = {}
        self._last_light: Optional[str] = None
        self.sent = 0

        if not self.dry_run:
            try:
                import serial
            except ImportError:
                raise SystemExit("--serial needs pyserial:  pip install pyserial")
            self._ser = serial.Serial(port, baud, timeout=0.2, write_timeout=1.0)
            time.sleep(2.0)
            log(f"[arm] connected {port} @ {baud}")

    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> int:
        return int(round(max(lo, min(hi, value))))

    def send(self, command: str) -> None:
        if self._ser is not None:
            try:
                self._ser.write(command.encode("ascii"))
                self._ser.flush()
            except Exception as exc:                              # noqa: BLE001
                log(f"[arm] write failed: {exc}")
                return
            log(f"[arm] -> {command}")
        else:
            print(f"[arm] -> {command}", file=sys.stderr, flush=True)

    def _emit(self, key: str, command: str, value: Optional[int] = None) -> None:
        if value is not None:
            if key in self._last and abs(value - self._last[key]) < self.deadband:
                return
            self._last[key] = value
        elif self._last.get(key) == command:
            return
        else:
            self._last[key] = command
        self.send(command)
        self.sent += 1

    def update(self, hand: Optional[Hand]) -> None:
        if hand is None or hand.gesture == "FIST":
            return
        now = time.monotonic()
        light = self.LIGHT_GESTURES.get(hand.gesture)
        if light and light != self._last_light:
            self._last_light = light
            self._emit("light", light)

        if now - self._last_send < self.period:
            return
        self._last_send = now

        wx, wy = float(hand.landmarks[0][0]), float(hand.landmarks[0][1])
        if self.mirror:
            wx = 1.0 - wx
        base = self._clamp(self.BASE_RANGE[0] + wx * (self.BASE_RANGE[1] - self.BASE_RANGE[0]),
                           *self.BASE_RANGE)
        elbow = self._clamp(self.ELBOW_RANGE[1] - wy * (self.ELBOW_RANGE[1] - self.ELBOW_RANGE[0]),
                            *self.ELBOW_RANGE)
        open_ratio = max(0.15, min(1.1, hand.pinch))
        head = self._clamp(self.HEAD_RANGE[0]
                           + (open_ratio - 0.15) / (1.1 - 0.15)
                           * (self.HEAD_RANGE[1] - self.HEAD_RANGE[0]), *self.HEAD_RANGE)

        self._emit("B", f"B{base}#", base)
        self._emit("E", f"E{elbow}#", elbow)
        self._emit("H", f"H{head}#", head)

    def close(self) -> None:
        if self._ser is not None:
            try:
                self._ser.close()
            except Exception:                                     # noqa: BLE001
                pass


# --------------------------------------------------------------------------- #
# Small utilities
# --------------------------------------------------------------------------- #

def probe_cameras(max_index: int = 5) -> List[int]:
    found = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ok, frame = cap.read()
            if ok and frame is not None:
                found.append(index)
                h, w = frame.shape[:2]
                print(f"camera {index}: {w}x{h}")
        cap.release()
    if not found:
        print("no working camera found (0..%d)" % (max_index - 1))
    return found


def resolve_source(source: Optional[str]) -> Tuple[str, object]:
    if source is None or source == "":
        return "camera", 0
    if source.isdigit():
        return "camera", int(source)
    if not os.path.exists(source):
        raise SystemExit(f"source not found: {source}")
    ext = os.path.splitext(source)[1].lower()
    if ext in (".mp4", ".avi", ".mov", ".mkv", ".m4v", ".webm"):
        return "video", source
    return "image", source


def csv_header() -> List[str]:
    """Column names for --csv: one row per hand per frame."""
    head = ["frame", "time_s", "label", "score", "gesture", "pinch"]
    head += [f"p{i}{axis}" for i in range(21) for axis in ("x", "y", "z")]
    return head


def hand_to_dict(hand: Hand, digits: int = 4) -> dict:
    return {
        "label": hand.label,
        "score": round(float(hand.score), 4),
        "gesture": hand.gesture,
        "pinch": round(float(hand.pinch), 4),
        "fingers": dict(zip(FINGER_NAMES, (bool(f) for f in hand.fingers))),
        "seen_tips": sorted(int(i) for i in hand.tips),
        "landmarks": [[round(float(v), digits) for v in row] for row in hand.landmarks],
        "world_landmarks": None,
    }


class GestureDebouncer:
    def __init__(self, window: int = 5) -> None:
        self.buf: Deque[str] = deque(maxlen=max(1, int(window)))
        self.current = "NONE"

    def __call__(self, gesture: Optional[str]) -> str:
        if gesture is None:
            self.buf.clear()
            self.current = "NONE"
            return self.current
        self.buf.append(gesture)
        counts: dict = {}
        for g in self.buf:
            counts[g] = counts.get(g, 0) + 1
        best = max(counts, key=counts.get)
        if counts[best] * 2 >= len(self.buf):
            self.current = best
        return self.current


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hand_landmarker_cv.py",
        description="21 hand landmarks with OpenCV only — no MediaPipe, no model file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples\n"
            "  python hand_landmarker_cv.py\n"
            "  python hand_landmarker_cv.py --calibrate          # learn the empty room\n"
            "  python hand_landmarker_cv.py --image hand.jpg --out marked.jpg --json\n"
            "  python hand_landmarker_cv.py --debug-mask\n"
            "  python hand_landmarker_cv.py --serial COM5 --baud 9600\n"
            "  python hand_landmarker_cv.py --dry-run\n"
        ),
    )
    p.add_argument("--source", default=None,
                   help="camera index (0, 1, ...), video path, or image path. Default: 0")
    p.add_argument("--camera", type=int, default=None, help="shorthand for --source N")
    p.add_argument("--image", default=None, help="shorthand: process a single image")
    p.add_argument("--video", default=None, help="shorthand: process a video file")
    p.add_argument("--width", type=int, default=1280, help="camera width (default 1280)")
    p.add_argument("--height", type=int, default=720, help="camera height (default 720)")
    p.add_argument("--calibrate", action="store_true",
                   help="capture ~40 empty-scene frames first, then subtract the room")
    p.add_argument("--calibrate-frames", type=int, default=40, help="frames to learn (40)")
    p.add_argument("--min-area", type=float, default=0.02,
                   help="smallest hand blob as a fraction of the frame (0.02)")
    p.add_argument("--smooth", type=float, default=0.45,
                   help="landmark smoothing 0..1, 0 = off (0.45)")

    o = p.add_argument_group("output")
    o.add_argument("--out", default=None, help="image mode: annotated image to write")
    o.add_argument("--record", default=None, help="write annotated video")
    o.add_argument("--json", action="store_true", help="print one JSON line per frame")
    o.add_argument("--csv", default=None, help="append landmark rows to a CSV")
    o.add_argument("--no-window", action="store_true", help="headless")
    o.add_argument("--show", action="store_true", help="force a window for files too")
    o.add_argument("--no-mirror", action="store_true", help="do not mirror the camera")
    o.add_argument("--indices", action="store_true", help="draw landmark indices")
    o.add_argument("--bbox", action="store_true", help="draw a bounding box")
    o.add_argument("--trail", action="store_true", help="fingertip trail")
    o.add_argument("--debug-mask", action="store_true", help="show the skin mask inset")
    o.add_argument("--stats", action="store_true", help="print fps every couple of seconds")
    o.add_argument("--gesture-window", type=int, default=5,
                   help="frames of majority vote for gestures (5)")
    o.add_argument("--quiet", action="store_true", help="suppress diagnostics")

    a = p.add_argument_group("robot arm (HC-05)")
    a.add_argument("--serial", default=None, help="serial port, e.g. COM5")
    a.add_argument("--baud", type=int, default=9600, help="HC-05 baud (9600)")
    a.add_argument("--send-hz", type=float, default=12.0, help="max commands per second (12)")
    a.add_argument("--deadband", type=int, default=2, help="min change to send (2)")
    a.add_argument("--dry-run", action="store_true", help="print commands, send nothing")

    m = p.add_argument_group("misc")
    m.add_argument("--probe", action="store_true", help="list working cameras and exit")
    m.add_argument("--version", action="version", version=f"hand_landmarker_cv.py {VERSION}")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    global QUIET
    args = build_parser().parse_args(argv)
    QUIET = bool(args.quiet)

    if args.probe:
        probe_cameras()
        return 0

    source = args.image or args.video or args.source
    if args.camera is not None:
        source = str(args.camera)
    kind, value = resolve_source(source if source is not None else "0")

    mirror = (not args.no_mirror) if kind == "camera" else False
    show_window = args.show or (not args.no_window and kind == "camera")
    if show_window and not hasattr(cv2, "imshow"):
        log("[cv] this OpenCV build has no GUI (headless) — running without a window")
        show_window = False

    segmenter = HandSegmenter(min_area_fraction=args.min_area,
                              background_frames=args.calibrate_frames)
    detector = CVHandDetector(segmenter=segmenter, min_area_fraction=args.min_area,
                              smooth=args.smooth)
    debouncer = GestureDebouncer(args.gesture_window)

    arm: Optional[ArmController] = None
    if args.serial or args.dry_run:
        arm = ArmController(port=args.serial, baud=args.baud, dry_run=args.dry_run,
                            hz=args.send_hz, mirror=mirror, deadband=args.deadband)

    def annotate(frame: np.ndarray, hands: Sequence[Hand], *, hud: Optional[Sequence[str]],
                 labels: bool = True, bbox: bool = False, indices: bool = False,
                 trail: Optional[Sequence[Tuple[int, int]]] = None,
                 mask: Optional[np.ndarray] = None, help_lines: bool = False) -> None:
        if trail and len(trail) > 1:
            draw_trail(frame, trail)
        for hand in hands:
            draw_hand(frame, hand, show_labels=labels, show_indices=indices,
                      show_bbox=bbox, show_seen=True)
        if mask is not None:
            draw_mask(frame, mask)
        if hud:
            draw_hud(frame, hud, show_help=help_lines)

    # ---- single image ------------------------------------------------------ #
    if kind == "image":
        frame = cv2.imread(str(value))
        if frame is None:
            raise SystemExit(f"could not read image: {value}")
        hands = detector.detect(frame, mirror=False)
        for hand in hands:
            hand.gesture = debouncer(hand.gesture)
            if arm is not None:
                arm.update(hand)

        hud = [f"single image   {frame.shape[1]}x{frame.shape[0]}"]
        hud += [f"hand: {h.label}  {h.gesture}  pinch {h.pinch:.2f}" for h in hands]
        if not hands:
            hud.append("no hand found — plain background? try --calibrate")
        annotate(frame, hands, hud=hud, bbox=args.bbox, indices=args.indices,
                 mask=segmenter.mask(frame) if args.debug_mask else None)

        if args.out:
            cv2.imwrite(args.out, frame)
            log(f"[cv] wrote {args.out}")
        if args.csv:
            new_file = not os.path.exists(args.csv) or os.path.getsize(args.csv) == 0
            with open(args.csv, "a", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                if new_file:
                    writer.writerow(csv_header())
                for hand in hands:
                    flat = [round(float(v), 5) for v in hand.landmarks.reshape(-1)]
                    writer.writerow([0, 0.0, hand.label, round(float(hand.score), 4),
                                     hand.gesture, round(hand.pinch, 4)] + flat)
            log(f"[cv] appended to {args.csv}")
        if show_window:
            cv2.imshow("hand_landmarker_cv", frame)
            log("[cv] press any key to close")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        payload = {
            "source": str(value),
            "width": int(frame.shape[1]),
            "height": int(frame.shape[0]),
            "engine": "opencv-geometry",
            "hands": [hand_to_dict(h) for h in hands],
        }
        if args.json or not args.out:
            print(json.dumps(payload, indent=None if args.json else 2))
        if arm:
            arm.close()
        return 0

    # ---- camera / video ---------------------------------------------------- #
    cap = cv2.VideoCapture(int(value) if kind == "camera" else str(value))
    if not cap.isOpened():
        raise SystemExit(f"could not open {kind}: {value}"
                         + ("  (try --probe)" if kind == "camera" else ""))
    if kind == "camera":
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    csv_writer = None
    csv_file = None
    if args.csv:
        new_file = not os.path.exists(args.csv) or os.path.getsize(args.csv) == 0
        csv_file = open(args.csv, "a", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        if new_file:
            csv_writer.writerow(csv_header())

    writer: Optional[cv2.VideoWriter] = None
    fps_marks: Deque[float] = deque(maxlen=60)
    trail: Deque[Tuple[int, int]] = deque(maxlen=32)
    frame_index = 0
    paused = False
    show_labels = True
    show_hud = True
    show_bbox = bool(args.bbox)
    show_trail = bool(args.trail)
    started = time.time()
    last_stats = time.time()
    fps = 0.0

    if args.calibrate:
        segmenter.start_calibration()
        log(f"[cv] calibrating: keep your hand (and face) out of frame for "
            f"{args.calibrate_frames} frames")

    try:
        while True:
            if not paused:
                ok, frame = cap.read()
                if not ok or frame is None:
                    log("[cv] end of stream")
                    break
                if mirror:
                    frame = cv2.flip(frame, 1)

                now = time.perf_counter()
                fps_marks.append(now)
                while len(fps_marks) > 2 and now - fps_marks[0] > 1.0:
                    fps_marks.popleft()
                fps = ((len(fps_marks) - 1) / (fps_marks[-1] - fps_marks[0])
                       if len(fps_marks) > 2 and fps_marks[-1] > fps_marks[0] else 0.0)
                elapsed = time.time() - started

                mask = segmenter.mask(frame)
                if segmenter.calibrating:
                    collected = segmenter.feed_calibration(frame)
                    hands: List[Hand] = []
                    hud = [f"calibrating {collected}/{args.calibrate_frames}",
                           "keep hand and face out of frame"]
                else:
                    hands = detector.detect(frame, mirror=mirror)
                    for hand in hands:
                        hand.gesture = debouncer(hand.gesture)
                        if arm is not None:
                            arm.update(hand)
                    hud = [f"{fps:5.1f} fps   {frame.shape[1]}x{frame.shape[0]}",
                           f"hand: {'yes' if hands else 'no'}   "
                           f"{'calibrated' if segmenter.background is not None else 'skin only'}"]
                    hud += [f"{h.label}  {h.gesture}  pinch {h.pinch:.2f}" for h in hands]

                trail.clear()
                for hand in hands:
                    trail.append(hand.px(8, frame.shape[1], frame.shape[0]))
                    if csv_writer is not None:
                        flat = [round(float(v), 5) for v in hand.landmarks.reshape(-1)]
                        csv_writer.writerow([frame_index, round(elapsed, 4), hand.label,
                                             round(float(hand.score), 4), hand.gesture,
                                             round(hand.pinch, 4)] + flat)
                if args.json:
                    print(json.dumps({"frame": frame_index, "t": round(elapsed, 4),
                                      "hands": [hand_to_dict(h) for h in hands]}), flush=True)

                annotate(frame, hands, hud=hud if show_hud else None, labels=show_labels,
                         bbox=show_bbox, indices=args.indices,
                         trail=trail if show_trail else None,
                         mask=mask if args.debug_mask else None, help_lines=show_window)
                frame_index += 1

                if writer is None and args.record and frame_index == 1:
                    src_fps = cap.get(cv2.CAP_PROP_FPS)
                    out_fps = src_fps if 1 <= src_fps <= 120 else 30.0
                    writer = cv2.VideoWriter(args.record, cv2.VideoWriter_fourcc(*"mp4v"),
                                             out_fps, (frame.shape[1], frame.shape[0]))
                    log(f"[cv] recording -> {args.record}")
                if writer is not None:
                    writer.write(frame)

                if args.stats and now - last_stats > 2.0 and fps > 0:
                    last_stats = now
                    log(f"[stats] {fps:5.1f} fps | hand {'yes' if hands else 'no'}")

            if show_window:
                cv2.imshow("hand_landmarker_cv", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
                if key == ord("c"):
                    if segmenter.background is not None:
                        segmenter.clear_background()
                        log("[cv] background calibration cleared — skin threshold only")
                    else:
                        segmenter.start_calibration()
                        log("[cv] calibrating: keep hand and face out of frame")
                elif key == ord("m"):
                    mirror = not mirror
                    if arm is not None:
                        arm.mirror = mirror
                elif key == ord("b"):
                    show_bbox = not show_bbox
                elif key == ord("k"):
                    show_trail = not show_trail
                elif key == ord("g"):
                    show_labels = not show_labels
                elif key == ord("h"):
                    show_hud = not show_hud
                elif key == ord("i"):
                    args.indices = not args.indices
                elif key == ord("s"):
                    name = time.strftime("snapshot_%Y%m%d_%H%M%S.png")
                    cv2.imwrite(name, frame)
                    log(f"[cv] saved {name}")
                elif key == ord(" "):
                    paused = not paused
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        if writer is not None:
            writer.release()
        if csv_file is not None:
            csv_file.close()
        if show_window:
            cv2.destroyAllWindows()
        if arm is not None:
            log(f"[arm] {arm.sent} command(s) sent")
            arm.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
