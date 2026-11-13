#!/usr/bin/env python3
"""
hand_landmarker.py — one-file, pure-Python hand landmarker.

Replicates what MediaPipe's `hand_landmarker.task` bundle does — 21 3-D hand
landmarks, left/right handedness, per-hand score — from a single .py file, then
adds the parts the demo leaves out: adaptive smoothing, gesture recognition,
teachable custom signs, and a robot-arm bridge.

Two backends, both inside the `mediapipe` wheel:

  solutions  (default)  mediapipe.solutions.hands. The trained hand-landmark
                        model ships inside the pip package, so there is NO
                        .task file to download and no extra asset at all.
  tasks                 mediapipe.tasks.python.vision.HandLandmarker, i.e. the
                        exact .task bundle path. Used automatically when a
                        hand_landmarker.task file is present, or downloaded
                        when you pass --backend tasks (needs internet once).

The model itself (millions of trained weights) cannot be reproduced by
rewriting code — what this file reproduces is the pipeline around it: the same
21 landmarks, same order, same normalised coordinates.

Quick start
-----------
    pip install -r requirements.txt
    python hand_landmarker.py                     # webcam, window
    python hand_landmarker.py --fast               # 640x480, lite model, 1 hand
    python hand_landmarker.py --source photo.jpg --out marked.jpg --json
    python hand_landmarker.py --dry-run            # see the arm commands
    python hand_landmarker.py --teach THUMB --teach-auto 25   # teach a new sign

Output: 21 landmarks per hand, normalised (x, y in 0..1, z relative to wrist),
plus optional world landmarks in metres, gestures, and Arduino commands for the
robot arm over classic Bluetooth (--serial COM5 --baud 9600).

MIT-style: do whatever you want with it.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
import threading
import time
import urllib.request
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Sequence, Tuple

# Silence MediaPipe / TensorFlow C++ chatter before importing them.
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np  # noqa: E402

try:
    import cv2  # noqa: E402
except ImportError:  # pragma: no cover - guidance only
    sys.exit("OpenCV is missing. Run:  pip install opencv-python")

QUIET = False
VERSION = "1.1.0"


def log(*parts: object) -> None:
    """Diagnostics go to stderr so stdout stays machine-readable."""
    if not QUIET:
        print(*parts, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

# Official MediaPipe model URLs (same file the web/Android demos fetch).
MODEL_URLS = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task",
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task",
)
DEFAULT_MODEL_NAME = "hand_landmarker.task"
DEFAULT_GESTURE_FILE = "gestures.json"

# Bone list, exactly the MediaPipe hand topology (21 points, 21 bones).
HAND_CONNECTIONS: Tuple[Tuple[int, int], ...] = (
    (0, 1), (1, 2), (2, 3), (3, 4),            # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),            # index
    (5, 9), (9, 10), (10, 11), (11, 12),       # middle
    (9, 13), (13, 14), (14, 15), (15, 16),     # ring
    (13, 17), (17, 18), (18, 19), (19, 20),    # pinky
    (0, 17),                                    # palm base
)

FINGER_NAMES = ("thumb", "index", "middle", "ring", "pinky")
# (mcp, pip, dip, tip) — thumb is (cmc, mcp, ip, tip)
FINGER_CHAINS = ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16), (17, 18, 19, 20))

LANDMARK_NAMES = (
    "wrist",
    "thumb_cmc", "thumb_mcp", "thumb_ip", "thumb_tip",
    "index_mcp", "index_pip", "index_dip", "index_tip",
    "middle_mcp", "middle_pip", "middle_dip", "middle_tip",
    "ring_mcp", "ring_pip", "ring_dip", "ring_tip",
    "pinky_mcp", "pinky_pip", "pinky_dip", "pinky_tip",
)

GESTURES = (
    "NONE", "FIST", "OPEN_PALM", "POINT", "PEACE", "THREE", "FOUR",
    "THUMBS_UP", "THUMBS_DOWN", "PINCH", "OK", "GUN",
)

# BGR colours
C_BONE = (200, 200, 200)
C_JOINT = (255, 255, 255)
C_TIP = (80, 220, 255)
C_TEXT = (255, 255, 255)
C_ACCENT = (90, 230, 120)
C_CUSTOM = (60, 200, 255)
C_DARK = (20, 20, 20)
C_BOX = (0, 200, 255)
FINGER_COLORS = {
    0: (60, 120, 240),    # thumb  – orange
    1: (90, 220, 110),    # index  – green
    2: (250, 200, 60),    # middle – cyan/blue
    3: (210, 90, 220),    # ring   – magenta
    4: (70, 70, 250),     # pinky  – red
}
POINT_FINGER = (0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4)
POINT_IS_TIP = {c[3] for c in FINGER_CHAINS}


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #

@dataclass
class Hand:
    landmarks: np.ndarray                      # (21, 3) normalised image coords
    world: Optional[np.ndarray]                # (21, 3) metres, or None
    label: str                                 # "Left" / "Right"
    score: float
    gesture: str = "NONE"
    pinch: float = 1.0
    fingers: Tuple[bool, ...] = (False,) * 5
    custom_label: Optional[str] = None
    custom_confidence: float = 0.0

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
# Gesture geometry (no model involved — pure landmarks)
# --------------------------------------------------------------------------- #

def _angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """Angle ABC in degrees between the two 2-D vectors."""
    v1, v2 = a - b, c - b
    n = float(np.linalg.norm(v1) * np.linalg.norm(v2))
    if n < 1e-9:
        return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(v1, v2)) / n))))


def _dist(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def analyse(landmarks: np.ndarray, aspect: float) -> Tuple[str, float, Tuple[bool, ...]]:
    """Return (gesture, pinch ratio, five finger-extended flags).

    Angles are rotation invariant, so this keeps working when the hand is
    sideways or upside down (the cvzone-style `tip.y < pip.y` test does not).
    Coordinates are scaled by the frame aspect ratio first, otherwise a wide
    webcam frame would squash the geometry.
    """
    p = landmarks[:, :2].astype(np.float32).copy()
    p[:, 0] *= aspect
    scale = max(_dist(p[0], p[9]), 1e-6)          # wrist -> middle MCP
    palm = p / scale                               # palm-normalised

    straight = []
    for finger, (mcp, pip, dip, tip) in enumerate(FINGER_CHAINS):
        base = _angle(palm[mcp], palm[pip], palm[tip])
        tip_far = _dist(palm[tip], palm[0]) > _dist(palm[pip], palm[0]) * 0.92
        if finger == 0:                            # thumb: use both joints
            extended = _angle(palm[1], palm[2], palm[3]) > 140 and _angle(palm[2], palm[3], palm[4]) > 145
        else:
            extended = base > 150 and tip_far
        straight.append(bool(extended))

    thumb, index, middle, ring, pinky = straight
    pinch = _dist(palm[4], palm[8])                # thumb tip <-> index tip
    # In a closed fist the thumb tip also sits next to the index tip, so a small
    # pinch only means "pinching" when the index reaches away from its knuckle.
    index_reach = _dist(palm[8], palm[5])          # index tip <-> index MCP
    pinching = pinch < 0.42 and index_reach > 0.5

    # A thumb that points up/down, with the other fingers closed, is a direction,
    # not an openness — compare tip and MCP vertically in image space.
    thumb_up = thumb and p[4][1] < p[2][1] - 0.25 * scale
    thumb_down = thumb and p[4][1] > p[2][1] + 0.25 * scale

    if pinching:
        gesture = "OK" if (middle and ring) else "PINCH"
    elif index and middle and not ring and not pinky:
        gesture = "GUN" if thumb else "PEACE"
    elif index and not middle and not ring and not pinky:
        gesture = "POINT"
    elif index and middle and ring and not pinky:
        gesture = "THREE"
    elif index and middle and ring and pinky:
        gesture = "OPEN_PALM" if thumb else "FOUR"
    elif not index and not middle and not ring and not pinky:
        gesture = "THUMBS_UP" if thumb_up else "THUMBS_DOWN" if thumb_down else "FIST"
    else:
        gesture = "NONE"

    return gesture, float(pinch), tuple(straight)


def _aspect_of(frame_bgr: np.ndarray) -> float:
    h, w = frame_bgr.shape[:2]
    return (w / h) if h else 1.0


# --------------------------------------------------------------------------- #
# Teachable gestures — palm-frame features + nearest neighbour
# --------------------------------------------------------------------------- #

def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return (v / n).astype(np.float32) if n > 1e-9 else v.astype(np.float32)


def hand_features(landmarks: np.ndarray, world: Optional[np.ndarray] = None,
                  aspect: float = 1.0) -> np.ndarray:
    """63 numbers: every landmark in a hand-aligned, scale-free frame.

    Borrowed in spirit from Kazuhito00's `pre_process_landmark` (wrist-relative,
    max-abs normalised), but rotated into the palm's own basis so a sign looks
    the same whether the hand is upright, sideways, or pointing at the lens.
    Uses the metric world landmarks when MediaPipe provides them.

    Layout: x0..x20, y0..y20, z0..z20 (wrist-relative, divided by palm length).
    """
    if world is not None and np.isfinite(world).all():
        pts = np.asarray(world, dtype=np.float32)
    else:
        pts = np.asarray(landmarks, dtype=np.float32).copy()
        pts[:, 0] *= aspect
        pts[:, 2] *= aspect

    origin = pts[0]
    vx = pts[5] - origin                            # wrist -> index knuckle
    if np.linalg.norm(vx) < 1e-6:
        vx = pts[9] - origin
    vx = _unit(vx)
    vz = np.cross(vx, pts[17] - origin)             # wrist -> pinky knuckle
    if np.linalg.norm(vz) < 1e-6:
        vz = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    vz = _unit(vz)
    vy = _unit(np.cross(vz, vx))

    local = (pts - origin) @ np.stack([vx, vy, vz]).T
    local = local / max(float(np.linalg.norm(local[9])), 1e-6)
    return local.reshape(-1).astype(np.float32)


class CustomGestures:
    """Nearest-neighbour gesture memory — no TensorFlow, no training script.

    Kazuhito00's sample trains a small MLP on logged landmarks; this does the
    same job with 40 lines of numpy: store examples, compare with the distance
    between unit feature vectors, majority-vote over the k closest, and refuse
    anything further away than `max_distance`. Add ~20 examples per sign.
    """

    def __init__(self, k: int = 5, threshold: float = 0.55,
                 max_distance: float = 0.35) -> None:
        self.k = max(1, int(k))
        self.threshold = float(threshold)
        self.max_distance = float(max_distance)
        self.samples: Dict[str, List[np.ndarray]] = {}

    # -- data --------------------------------------------------------------- #
    @property
    def enabled(self) -> bool:
        return any(self.samples.values())

    @property
    def labels(self) -> List[str]:
        return sorted(self.samples)

    def count(self, name: str) -> int:
        return len(self.samples.get(name, ()))

    def add(self, name: str, features: np.ndarray) -> int:
        self.samples.setdefault(name, []).append(_unit(np.asarray(features, np.float32)))
        return self.count(name)

    def clear(self, name: Optional[str] = None) -> None:
        if name is None:
            self.samples.clear()
        else:
            self.samples.pop(name, None)

    # -- inference ---------------------------------------------------------- #
    def classify(self, features: np.ndarray) -> Tuple[Optional[str], float]:
        """Return (label, confidence). (None, 0.0) when nothing is close enough."""
        if not self.enabled:
            return None, 0.0
        q = _unit(np.asarray(features, np.float32))
        # Both sides are unit vectors, so this is the chord length: 0 = identical
        # pose, 0.4ish = a different hand shape. (Cosine alone is far too
        # forgiving here — an open palm and a fist are only 0.09 apart.)
        ranked: List[Tuple[float, str]] = []
        for name, samples in self.samples.items():
            for sample in samples:
                ranked.append((float(np.linalg.norm(q - sample)), name))
        if not ranked:
            return None, 0.0
        ranked.sort(key=lambda item: item[0])
        if ranked[0][0] > self.max_distance:
            return None, 0.0

        votes: Dict[str, float] = {}
        for distance, name in ranked[: self.k]:
            votes[name] = votes.get(name, 0.0) + 1.0 / (distance + 1e-3)
        best = max(votes, key=votes.get)
        confidence = votes[best] / sum(votes.values())
        if confidence < self.threshold:
            return None, confidence
        return best, confidence

    # -- persistence -------------------------------------------------------- #
    def save(self, path: str) -> None:
        payload = {
            "version": 1,
            "feature": "palm-frame-63",
            "gestures": {
                name: [[round(float(v), 6) for v in sample] for sample in samples]
                for name, samples in self.samples.items()
            },
        }
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1)
        os.replace(tmp, path)

    @classmethod
    def load(cls, path: str, k: int = 5, threshold: float = 0.55,
             max_distance: float = 0.35, quiet: bool = False) -> "CustomGestures":
        gestures = cls(k=k, threshold=threshold, max_distance=max_distance)
        if not os.path.exists(path):
            return gestures
        try:
            with open(path, encoding="utf-8") as fh:
                payload = json.load(fh)
            if payload.get("feature") != "palm-frame-63":
                raise ValueError("unexpected feature layout")
            for name, samples in payload.get("gestures", {}).items():
                for sample in samples:
                    vec = np.asarray(sample, dtype=np.float32)
                    if vec.size != 63:
                        raise ValueError(f"{name}: expected 63 numbers, got {vec.size}")
                    gestures.samples.setdefault(name, []).append(_unit(vec))
        except Exception as exc:                        # noqa: BLE001 - never fatal
            if not quiet:
                log(f"[hand_landmarker] ignoring {path}: {exc}")
            return cls(k=k, threshold=threshold, max_distance=max_distance)
        return gestures


# --------------------------------------------------------------------------- #
# Backends
# --------------------------------------------------------------------------- #

class HandTracker:
    """Uniform wrapper over mediapipe's solutions and tasks APIs."""

    def __init__(self, backend: str = "auto", model_path: Optional[str] = None,
                 max_hands: int = 2, min_detection: float = 0.5,
                 min_tracking: float = 0.5, complexity: int = 1,
                 streaming: bool = True, allow_download: bool = True,
                 delegate: str = "cpu") -> None:
        self.max_hands = max(1, int(max_hands))
        self.streaming = streaming
        self.delegate = delegate
        self.backend = self._choose(backend, model_path, allow_download)
        self._ts = 0
        self._last_ts = 0

        if self.backend == "tasks":
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision

            self._opts = dict(
                running_mode=vision.RunningMode.VIDEO if streaming else vision.RunningMode.IMAGE,
                num_hands=self.max_hands,
                min_hand_detection_confidence=float(min_detection),
                min_hand_presence_confidence=float(min_detection),
                min_tracking_confidence=float(min_tracking),
            )
            self._vision = vision
            self._base_options = mp_python.BaseOptions
            self._mp_image = None
            self._lm = self._create_task(self.delegate)
        else:
            import mediapipe as mp

            self._hands = mp.solutions.hands.Hands(
                static_image_mode=not streaming,
                max_num_hands=self.max_hands,
                model_complexity=int(complexity),
                min_detection_confidence=float(min_detection),
                min_tracking_confidence=float(min_tracking),
            )
        if delegate == "gpu" and self.backend == "solutions":
            log("[hand_landmarker] --delegate gpu only applies to the tasks backend; using CPU")
        log(f"[hand_landmarker] backend={self.backend}"
            + (f" model={self.model_path} delegate={self.delegate}" if self.backend == "tasks"
               else " (model bundled in mediapipe)"))

    def _create_task(self, delegate: str):
        """Build the Tasks landmarker; fall back to CPU if the GPU is unusable."""
        BaseOptions = self._base_options
        vision = self._vision
        order = ["GPU", "CPU"] if delegate == "gpu" else ["CPU"]
        last_error: Optional[Exception] = None
        for kind in order:
            try:
                base = BaseOptions(model_asset_path=self.model_path,
                                   delegate=BaseOptions.Delegate.GPU if kind == "GPU"
                                   else BaseOptions.Delegate.CPU)
                landmarker = vision.HandLandmarker.create_from_options(
                    vision.HandLandmarkerOptions(base_options=base, **self._opts))
                self.delegate = kind.lower()
                return landmarker
            except Exception as exc:                    # noqa: BLE001 - try CPU next
                last_error = exc
                log(f"[hand_landmarker] {kind} delegate unavailable: {exc}")
        raise SystemExit(f"could not create the hand landmarker: {last_error}")

    # -- backend selection -------------------------------------------------- #
    def _choose(self, backend: str, model_path: Optional[str], allow_download: bool) -> str:
        if backend not in ("auto", "solutions", "tasks"):
            raise SystemExit(f"unknown backend {backend!r}")
        if backend == "solutions":
            return "solutions"

        candidate = model_path or (DEFAULT_MODEL_NAME if os.path.exists(DEFAULT_MODEL_NAME) else None)
        if backend == "tasks":
            candidate = candidate or (DEFAULT_MODEL_NAME if allow_download else None)
            if candidate is None:
                raise SystemExit(
                    "The tasks backend needs hand_landmarker.task. Pass --model PATH, "
                    "or drop the file next to this script, or allow the download."
                )
            self.model_path = self._ensure_model(candidate, allow_download)
            return "tasks"

        # auto: use the exact .task bundle only when it is already available.
        if candidate and os.path.exists(candidate):
            self.model_path = candidate
            return "tasks"
        if os.path.exists(DEFAULT_MODEL_NAME):
            self.model_path = DEFAULT_MODEL_NAME
            return "tasks"
        return "solutions"

    @staticmethod
    def _ensure_model(path: str, allow_download: bool) -> str:
        if os.path.exists(path) and os.path.getsize(path) > 1_000_000:
            return path
        if not allow_download:
            raise SystemExit(f"model not found: {path}")
        target = path if os.path.isabs(path) or os.sep in path else os.path.abspath(path)
        log(f"[hand_landmarker] downloading {os.path.basename(target)} (~8 MB, once) …")
        last_error: Optional[Exception] = None
        for url in MODEL_URLS:
            try:
                with urllib.request.urlopen(url, timeout=60) as resp:
                    data = resp.read()
                if len(data) < 1_000_000:
                    raise IOError("file too small — download truncated")
                with open(target, "wb") as fh:
                    fh.write(data)
                log(f"[hand_landmarker] saved {target} ({len(data)/1e6:.1f} MB)")
                return target
            except Exception as exc:                 # noqa: BLE001 - try next mirror
                last_error = exc
                log(f"[hand_landmarker] mirror failed ({url.split('/')[2]}): {exc}")
        raise SystemExit(
            f"could not download the model ({last_error}).\n"
            "Download it in a browser and point at it:\n"
            "  python hand_landmarker.py --backend tasks --model C:\\path\\hand_landmarker.task\n"
            "or skip the .task file entirely with --backend solutions (default)."
        )

    # -- inference ---------------------------------------------------------- #
    def process(self, rgb: np.ndarray) -> List[Hand]:
        if self.backend == "solutions":
            rgb.flags.writeable = False              # avoids an internal copy
            result = self._hands.process(rgb)
            out: List[Hand] = []
            if not result.multi_hand_landmarks:
                return out
            worlds = result.multi_hand_world_landmarks or [None] * len(result.multi_hand_landmarks)
            labels = result.multi_handedness or [None] * len(result.multi_hand_landmarks)
            for lm, world, handed in zip(result.multi_hand_landmarks, worlds, labels):
                pts = np.array([[p.x, p.y, p.z] for p in lm.landmark], dtype=np.float32)
                wpts = (np.array([[p.x, p.y, p.z] for p in world.landmark], dtype=np.float32)
                        if world is not None else None)
                label = handed.classification[0].label if handed else "?"
                score = float(handed.classification[0].score) if handed else 0.0
                out.append(Hand(pts, wpts, label, score))
            return out

        import mediapipe as mp

        if self._mp_image is None:
            self._mp_image = mp.Image
        image = self._mp_image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
        if self.streaming:
            ts = int(time.monotonic() * 1000)
            if ts <= self._last_ts:
                ts = self._last_ts + 1
            self._last_ts = ts
            result = self._lm.detect_for_video(image, ts)
        else:
            result = self._lm.detect(image)

        out = []
        for i, lm in enumerate(result.hand_landmarks):
            pts = np.array([[p.x, p.y, p.z] for p in lm], dtype=np.float32)
            wpts = None
            if i < len(result.hand_world_landmarks) and result.hand_world_landmarks[i]:
                wpts = np.array([[p.x, p.y, p.z] for p in result.hand_world_landmarks[i]],
                                dtype=np.float32)
            label, score = "?", 0.0
            if i < len(result.handedness) and result.handedness[i]:
                label = result.handedness[i][0].category_name or "?"
                score = float(result.handedness[i][0].score)
            out.append(Hand(pts, wpts, label, score))
        return out

    def close(self) -> None:
        try:
            if self.backend == "solutions":
                self._hands.close()
            else:
                self._lm.close()
        except Exception:                            # noqa: BLE001 - best effort
            pass


# --------------------------------------------------------------------------- #
# Smoothing, debouncing, capture
# --------------------------------------------------------------------------- #

class OneEuroFilter:
    """Adaptive low-pass filter (Casiez, Roussel & Vogel, CHI 2012).

    A fixed-alpha EMA forces one trade-off: either jittery when still, or
    laggy when moving. This raises the cutoff as speed rises — heavy smoothing
    at rest, almost none on a fast swipe. Applied per coordinate.
    """

    def __init__(self, min_cutoff: float = 2.6, beta: float = 12.0,
                 d_cutoff: float = 1.0, enabled: bool = True) -> None:
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.enabled = enabled
        self._x: Optional[np.ndarray] = None
        self._dx: Optional[np.ndarray] = None
        self._t: Optional[float] = None

    @classmethod
    def from_strength(cls, strength: float) -> "OneEuroFilter":
        """Map --smooth 0..1 to filter parameters (0 disables smoothing)."""
        s = max(0.0, min(1.0, float(strength)))
        if s <= 0.0:
            return cls(enabled=False)
        # Measured on a synthetic 0.4 Hz hand sweep at 30 fps with 6 mm noise:
        # jitter drops ~2.5-3x and RMS error stays at or below the raw signal.
        return cls(min_cutoff=0.6 + 2.4 * (1.0 - s), beta=8.0 * s)

    @staticmethod
    def _alpha(cutoff: np.ndarray, dt: float) -> np.ndarray:
        tau = 1.0 / (2.0 * math.pi * np.maximum(cutoff, 1e-3))
        return 1.0 / (1.0 + tau / dt)

    def reset(self) -> None:
        self._x = self._dx = self._t = None

    def __call__(self, points: Optional[np.ndarray], t: float) -> Optional[np.ndarray]:
        if points is None:
            self.reset()
            return None
        if not self.enabled:
            return points
        p = np.asarray(points, dtype=np.float32)
        if self._x is None or self._x.shape != p.shape:
            self._x, self._dx, self._t = p.copy(), np.zeros_like(p), t
            return p

        dt = float(t - self._t)
        if not np.isfinite(dt) or dt <= 0:
            dt = 1.0 / 60.0
        dt = min(dt, 0.25)                            # after a stall, don't trust the slope
        derivative = (p - self._x) / dt
        a_d = self._alpha(np.array(self.d_cutoff), dt)
        self._dx = a_d * derivative + (1.0 - a_d) * self._dx
        cutoff = self.min_cutoff + self.beta * np.abs(self._dx)
        a = self._alpha(cutoff, dt)
        self._x = a * p + (1.0 - a) * self._x
        self._t = t
        return self._x


class GestureDebouncer:
    """Majority vote over the last `window` frames — kills one-frame flicker."""

    def __init__(self, window: int = 5) -> None:
        self.buf: Deque[str] = deque(maxlen=max(1, int(window)))
        self.current = "NONE"

    def __call__(self, gesture: Optional[str]) -> str:
        if gesture is None:
            self.buf.clear()
            self.current = "NONE"
            return self.current
        self.buf.append(gesture)
        if self.buf:
            counts: Dict[str, int] = {}
            for g in self.buf:
                counts[g] = counts.get(g, 0) + 1
            best = max(counts, key=counts.get)
            if counts[best] * 2 >= len(self.buf):
                self.current = best
        return self.current


class VideoStream:
    """Camera reader on a background thread.

    OpenCV's `read()` blocks until the next frame, so if inference is slower
    than the camera, frames queue and the preview drifts behind reality. A
    reader thread plus a single-slot buffer means you always get the newest
    frame and simply drop the ones you were too slow to use.
    """

    def __init__(self, index: int, width: Optional[int] = None,
                 height: Optional[int] = None, fps: float = 0.0) -> None:
        self.cap = cv2.VideoCapture(int(index))
        if not self.cap.isOpened():
            raise SystemExit(f"could not open camera: {index}  (try --probe)")
        if width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(width))
        if height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(height))
        if fps and fps > 0:
            self.cap.set(cv2.CAP_PROP_FPS, float(fps))
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self._lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._ok = False
        self._running = True
        self.dropped = 0
        self._thread = threading.Thread(target=self._reader, name="capture", daemon=True)
        self._thread.start()

    def _reader(self) -> None:
        while self._running:
            ok, frame = self.cap.read()
            with self._lock:
                if self._frame is not None:
                    self.dropped += 1                 # the previous frame was never used
                self._ok, self._frame = bool(ok), frame
            if not ok:
                time.sleep(0.02)

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        with self._lock:
            return self._ok, self._frame

    @property
    def size(self) -> Tuple[int, int]:
        return (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def release(self) -> None:
        self._running = False
        try:
            self._thread.join(timeout=0.5)
        except Exception:                            # noqa: BLE001
            pass
        self.cap.release()


# --------------------------------------------------------------------------- #
# Drawing
# --------------------------------------------------------------------------- #

def _line_thickness(height: int) -> int:
    return max(1, int(round(height / 320)))


def draw_hand(frame: np.ndarray, hand: Hand, *, show_points: bool = True,
              show_labels: bool = True, show_indices: bool = False,
              show_bbox: bool = False) -> None:
    h, w = frame.shape[:2]
    thick = _line_thickness(h)
    r = max(2, int(round(min(w, h) * 0.007)))

    if show_bbox:
        x1, y1, x2, y2 = hand.bbox(w, h, pad=int(min(w, h) * 0.03))
        cv2.rectangle(frame, (x1, y1), (x2, y2), C_DARK, thick + 3, cv2.LINE_AA)
        cv2.rectangle(frame, (x1, y1), (x2, y2), C_BOX, thick + 1, cv2.LINE_AA)

    for a, b in HAND_CONNECTIONS:
        color = FINGER_COLORS[POINT_FINGER[b]] if b not in (0, 5, 9, 13, 17) else C_BONE
        cv2.line(frame, hand.px(a, w, h), hand.px(b, w, h), color, thick, cv2.LINE_AA)

    if show_points:
        for i in range(21):
            x, y = hand.px(i, w, h)
            color = C_TIP if i in POINT_IS_TIP else C_JOINT
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


def draw_trail(frame: np.ndarray, points: Sequence[Tuple[int, int]]) -> None:
    """Fading fingertip trail — the cheap version of Kazuhito00's point history."""
    h = frame.shape[0]
    thick = max(2, _line_thickness(h) + 1)
    n = len(points)
    for i in range(1, n):
        fade = i / n
        color = (int(90 * fade), int(200 * fade), int(255 * fade))
        cv2.line(frame, points[i - 1], points[i], color, thick, cv2.LINE_AA)


def _text(frame: np.ndarray, text: str, org: Tuple[int, int], scale: float,
          color: Tuple[int, int, int] = C_TEXT, thick: int = 1) -> None:
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, C_DARK,
                thick + 2, cv2.LINE_AA)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                thick, cv2.LINE_AA)


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
        help_lines = [
            "q quit   s snapshot   m mirror   b box   k trail",
            "t teach   c custom gestures   h hud   i indices   space pause",
        ]
        y0 = h - pad - line_h * (len(help_lines) - 1) - pad
        for j, text in enumerate(help_lines):
            cv2.putText(frame, text, (10 + pad, y0 + j * line_h), cv2.FONT_HERSHEY_SIMPLEX,
                        scale * 0.8, C_TEXT, 1, cv2.LINE_AA)


def draw_pinch_bar(frame: np.ndarray, hand: Hand) -> None:
    """Small vertical bar near the wrist showing pinch openness 0..1."""
    h, w = frame.shape[:2]
    x, y = hand.px(0, w, h)
    x -= int(min(w, h) * 0.045)
    bar_h = int(min(w, h) * 0.12)
    bar_w = max(4, int(min(w, h) * 0.012))
    cv2.rectangle(frame, (x, y - bar_h // 2), (x + bar_w, y + bar_h // 2), C_DARK, -1)
    level = int(bar_h * min(1.0, hand.pinch / 1.2))
    cv2.rectangle(frame, (x, y + bar_h // 2 - level), (x + bar_w, y + bar_h // 2),
                  C_ACCENT, -1)


# --------------------------------------------------------------------------- #
# Robot-arm bridge (optional)
# --------------------------------------------------------------------------- #

class ArmController:
    """Turns hand landmarks into the arm's `B/E/H/TW/TN/TC#` protocol.

    Mapping (all clamped, dead-banded, rate limited):
      wrist x   -> base  B 0..300      (mirrored: left of screen = 0)
      wrist y   -> elbow E 30..150     (hand high = raised)
      pinch     -> head  H 45..135     (fingers together = closed)
      gestures  -> light  TW / TN / TC (once per change)
      FIST      -> freeze: nothing is sent, arm holds position
    """

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
            time.sleep(2.0)      # HC-05 needs a moment after the link opens
            log(f"[arm] connected {port} @ {baud}")

    # -- helpers ------------------------------------------------------------ #
    @staticmethod
    def _clamp(value: float, lo: float, hi: float) -> int:
        return int(round(max(lo, min(hi, value))))

    def send(self, command: str) -> None:
        if self._ser is not None:
            try:
                self._ser.write(command.encode("ascii"))
                self._ser.flush()
            except Exception as exc:                          # noqa: BLE001
                log(f"[arm] write failed: {exc}")
                return
            log(f"[arm] -> {command}")
        else:
            # Dry run: to stderr, so `--json` on stdout stays a clean event stream.
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

    # -- main hook ---------------------------------------------------------- #
    def update(self, hand: Optional[Hand]) -> None:
        if hand is None:
            return                                   # no hand: arm holds still
        if hand.gesture == "FIST":
            return                                   # deliberate freeze

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
            except Exception:                             # noqa: BLE001
                pass


# --------------------------------------------------------------------------- #
# I/O helpers
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


def resolve_source(source: str) -> Tuple[str, object]:
    """Return (kind, value) where kind is camera|video|image."""
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


def hand_to_dict(hand: Hand, digits: int = 4) -> dict:
    return {
        "label": hand.label,
        "score": round(float(hand.score), 4),
        "gesture": hand.gesture,
        "gesture_source": "custom" if hand.custom_label else "geometry",
        "gesture_confidence": round(float(hand.custom_confidence), 4),
        "pinch": round(float(hand.pinch), 4),
        "fingers": dict(zip(FINGER_NAMES, (bool(f) for f in hand.fingers))),
        "landmarks": [[round(float(v), digits) for v in row] for row in hand.landmarks],
        "world_landmarks": ([[round(float(v), digits) for v in row] for row in hand.world]
                            if hand.world is not None else None),
    }


def _gesture_lines(hands: Sequence[Hand], index: int) -> str:
    hand = hands[index]
    tag = " (custom)" if hand.custom_label else ""
    conf = f" {hand.custom_confidence:.2f}" if hand.custom_label else ""
    return f"H{index + 1} {hand.label:<5} {hand.gesture}{conf}{tag}"


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hand_landmarker.py",
        description="Pure-Python hand landmarker (21 points), gesture engine and robot-arm bridge.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples\n"
            "  python hand_landmarker.py\n"
            "  python hand_landmarker.py --fast\n"
            "  python hand_landmarker.py --source 1 --max-hands 1\n"
            "  python hand_landmarker.py --source hand.jpg --out marked.jpg --json\n"
            "  python hand_landmarker.py --serial COM5 --baud 9600\n"
            "  python hand_landmarker.py --dry-run                  # print arm commands, no serial\n"
            "  python hand_landmarker.py --teach ROCK --teach-auto 25\n"
            "  python hand_landmarker.py --probe                    # list working cameras\n"
        ),
    )
    p.add_argument("--source", default=None,
                   help="camera index (0, 1, ...), video path, or image path. Default: 0")
    p.add_argument("--camera", type=int, default=None, help="shorthand for --source N")
    p.add_argument("--image", default=None, help="shorthand: process a single image")
    p.add_argument("--video", default=None, help="shorthand: process a video file")
    # 1640x1232 is the IMX219's full-field-of-view binned mode. The old 1280x720
    # default was not a sensor mode at all, so V4L2 silently fell back to
    # 1920x1080, which crops a centre window and looked ~1.7x zoomed in.
    p.add_argument("--width", type=int, default=1640,
                   help="camera capture width (default 1640 = full sensor FoV)")
    p.add_argument("--height", type=int, default=1232,
                   help="camera capture height (default 1232 = full sensor FoV)")
    p.add_argument("--cam-fps", type=float, default=0.0, help="request a camera frame rate (0 = driver default)")
    p.add_argument("--max-hands", type=int, default=2, help="hands to track, 1-4 (default 2)")
    p.add_argument("--fast", action="store_true",
                   help="preset: lite model, 1 hand, 640x480 — roughly doubles fps")

    g = p.add_argument_group("model")
    g.add_argument("--backend", choices=("auto", "solutions", "tasks"), default="auto",
                   help="solutions = bundled model, no .task file (default auto)")
    g.add_argument("--model", default=None,
                   help=f"path to hand_landmarker.task (default: ./{DEFAULT_MODEL_NAME})")
    g.add_argument("--no-download", action="store_true", help="never fetch the .task file")
    g.add_argument("--complexity", type=int, choices=(0, 1), default=1,
                   help="solutions model: 0 = lite/fast, 1 = full/accurate (default 1)")
    g.add_argument("--delegate", choices=("cpu", "gpu"), default="cpu",
                   help="tasks backend: inference delegate (default cpu; falls back)")
    g.add_argument("--min-detection", type=float, default=0.5, help="detection confidence (0.5)")
    g.add_argument("--min-tracking", type=float, default=0.5, help="tracking confidence (0.5)")

    o = p.add_argument_group("output")
    o.add_argument("--out", default=None,
                   help="image mode: annotated image to write; video mode: --record instead")
    o.add_argument("--record", default=None, help="write annotated video (e.g. out.mp4)")
    o.add_argument("--json", action="store_true", help="print landmarks as JSON lines")
    o.add_argument("--csv", default=None, help="append landmark rows to a CSV file")
    o.add_argument("--no-window", action="store_true", help="headless: no preview window")
    o.add_argument("--show", action="store_true", help="force a preview window (even for files)")
    o.add_argument("--no-mirror", action="store_true", help="do not mirror the camera preview")
    o.add_argument("--indices", action="store_true", help="draw landmark indices 0-20")
    o.add_argument("--bbox", action="store_true", help="draw a bounding box around each hand")
    o.add_argument("--trail", action="store_true", help="draw a fading index-fingertip trail")
    o.add_argument("--stats", action="store_true", help="print capture/inference/draw timings")
    o.add_argument("--smooth", type=float, default=0.5,
                   help="smoothing strength 0..1, 0 = off (default 0.5)")
    o.add_argument("--gesture-window", type=int, default=5,
                   help="frames of majority vote for gestures (default 5)")
    o.add_argument("--quiet", action="store_true", help="suppress diagnostics on stderr")

    c = p.add_argument_group("custom gestures")
    c.add_argument("--custom", default=None,
                   help=f"gesture file (default ./{DEFAULT_GESTURE_FILE} if it exists)")
    c.add_argument("--no-custom", action="store_true", help="ignore a gestures file")
    c.add_argument("--teach", default=None, metavar="NAME",
                   help="teach a sign: press 't' to add samples, saved on the way out")
    c.add_argument("--teach-auto", type=int, default=0, metavar="N",
                   help="capture N samples automatically instead of pressing 't'")
    c.add_argument("--custom-threshold", type=float, default=0.55,
                   help="min vote share to accept a custom sign (0.55)")
    c.add_argument("--custom-k", type=int, default=5, help="neighbours to vote with (5)")
    c.add_argument("--custom-distance", type=float, default=0.35,
                   help="max cosine chord distance to accept a sign (0.35)")
    c.add_argument("--list-gestures", action="store_true", help="show taught signs and exit")

    a = p.add_argument_group("robot arm (HC-05)")
    a.add_argument("--serial", default=None, help="serial port, e.g. COM5 or /dev/rfcomm0")
    a.add_argument("--baud", type=int, default=9600, help="HC-05 baud (default 9600)")
    a.add_argument("--send-hz", type=float, default=12.0, help="max commands per second (12)")
    a.add_argument("--deadband", type=int, default=2, help="min angle change to send (2)")
    a.add_argument("--dry-run", action="store_true", help="print arm commands, send nothing")

    m = p.add_argument_group("misc")
    m.add_argument("--probe", action="store_true", help="list working camera indices and exit")
    m.add_argument("--version", action="version", version=f"hand_landmarker.py {VERSION}")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    global QUIET
    args = build_parser().parse_args(argv)
    QUIET = bool(args.quiet)

    if args.probe:
        probe_cameras()
        return 0

    gesture_path = args.custom or DEFAULT_GESTURE_FILE
    custom = CustomGestures.load(
        gesture_path, k=args.custom_k, threshold=args.custom_threshold,
        max_distance=args.custom_distance, quiet=not (args.teach or args.list_gestures),
    )
    if args.no_custom:
        custom = CustomGestures()

    if args.list_gestures:
        if not custom.enabled:
            print(f"no taught gestures in {gesture_path}")
        else:
            print(f"{gesture_path}:")
            for name in custom.labels:
                print(f"  {name:<20} {custom.count(name)} samples")
        return 0

    if args.teach_auto and not args.teach:
        raise SystemExit("--teach-auto needs --teach NAME")
    teaching = bool(args.teach)
    if teaching:
        log(f"[hand_landmarker] teaching '{args.teach}' -> {gesture_path}")
        if not args.teach_auto:
            log("[hand_landmarker] press t to add a sample (20+ per sign recommended)")

    if args.fast:
        args.complexity = 0
        args.max_hands = min(args.max_hands, 1)
        if args.width == 1640:
            args.width = 640
        if args.height == 1232:
            args.height = 480

    source = args.image or args.video or args.source
    if args.camera is not None:
        source = str(args.camera)
    kind, value = resolve_source(source if source is not None else "0")

    streaming = kind != "image"
    mirror = (not args.no_mirror) if kind == "camera" else False
    show_window = args.show or (not args.no_window and kind == "camera")

    if show_window and not hasattr(cv2, "imshow"):
        log("[hand_landmarker] this OpenCV build has no GUI (headless). "
            "Install 'opencv-python', or run with --no-window.")
        show_window = False

    smoother = OneEuroFilter.from_strength(args.smooth)
    debouncer = GestureDebouncer(args.gesture_window)

    arm: Optional[ArmController] = None
    if args.serial or args.dry_run:
        arm = ArmController(port=args.serial, baud=args.baud, dry_run=args.dry_run,
                            hz=args.send_hz, mirror=mirror, deadband=args.deadband)

    def annotate(hand_list: Sequence[Hand], *, labels: bool, indices: bool, bbox: bool,
                 trail_pts: Optional[Sequence[Tuple[int, int]]],
                 hud: Optional[Sequence[str]], help_lines: bool, frame: np.ndarray) -> None:
        if trail_pts and len(trail_pts) > 1:
            draw_trail(frame, trail_pts)
        for hand in hand_list:
            draw_pinch_bar(frame, hand)
        for hand in hand_list:
            draw_hand(frame, hand, show_labels=labels, show_indices=indices, show_bbox=bbox)
        if hud:
            draw_hud(frame, hud, show_help=help_lines)

    if teaching and kind == "image":
        log("[hand_landmarker] --teach needs a camera or video source, not a single image")
        teaching = False

    # ---- single image ------------------------------------------------------ #
    if kind == "image":
        frame = cv2.imread(str(value))
        if frame is None:
            raise SystemExit(f"could not read image: {value}")
        tracker = HandTracker(
            backend=args.backend, model_path=args.model, max_hands=args.max_hands,
            min_detection=args.min_detection, min_tracking=args.min_tracking,
            complexity=args.complexity, streaming=False,
            allow_download=not args.no_download, delegate=args.delegate,
        )
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hands = tracker.process(rgb)
        aspect = _aspect_of(frame)
        for hand in hands:
            pts = smoother(hand.landmarks, time.perf_counter())
            if pts is not None:
                hand.landmarks = pts
            hand.gesture, hand.pinch, hand.fingers = analyse(hand.landmarks, aspect)
            if custom.enabled:
                name, conf = custom.classify(
                    hand_features(hand.landmarks, hand.world, aspect))
                if name:
                    hand.gesture, hand.custom_label, hand.custom_confidence = name, name, conf
            if arm is not None:
                arm.update(hand)

        annotated = frame
        hud = ["single image", f"hands: {len(hands)}", f"backend: {tracker.backend}"]
        hud += [_gesture_lines(hands, i) for i in range(len(hands))]
        annotate(hands, labels=True, indices=args.indices, bbox=args.bbox,
                 trail_pts=None, hud=hud, help_lines=False, frame=annotated)

        if args.out:
            cv2.imwrite(args.out, annotated)
            log(f"[hand_landmarker] wrote {args.out}")
        if show_window:
            cv2.imshow("hand_landmarker", annotated)
            log("[hand_landmarker] press any key to close")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        payload = {
            "source": str(value),
            "width": int(frame.shape[1]),
            "height": int(frame.shape[0]),
            "backend": tracker.backend,
            "hands": [hand_to_dict(h) for h in hands],
        }
        if args.json or not args.out:
            print(json.dumps(payload, indent=None if args.json else 2))
        tracker.close()
        if arm:
            arm.close()
        return 0

    # ---- camera / video ---------------------------------------------------- #
    stream: Optional[VideoStream] = None
    cap: Optional[cv2.VideoCapture] = None
    if kind == "camera":
        stream = VideoStream(int(value), args.width, args.height, args.cam_fps)
        log(f"[hand_landmarker] camera {value}: {stream.size[0]}x{stream.size[1]}")
    else:
        cap = cv2.VideoCapture(str(value))
        if not cap.isOpened():
            raise SystemExit(f"could not open {kind}: {value}")

    tracker = HandTracker(
        backend=args.backend, model_path=args.model, max_hands=args.max_hands,
        min_detection=args.min_detection, min_tracking=args.min_tracking,
        complexity=args.complexity, streaming=streaming,
        allow_download=not args.no_download, delegate=args.delegate,
    )

    csv_writer = None
    csv_file = None
    if args.csv:
        new_file = not os.path.exists(args.csv) or os.path.getsize(args.csv) == 0
        csv_file = open(args.csv, "a", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        if new_file:
            header = ["frame", "time_s", "hand_index", "label", "score", "gesture", "pinch"]
            header += [f"p{i}{axis}" for i in range(21) for axis in ("x", "y", "z")]
            csv_writer.writerow(header)

    writer: Optional[cv2.VideoWriter] = None
    fps_marks: Deque[float] = deque(maxlen=90)
    trail: Deque[Tuple[int, int]] = deque(maxlen=32)
    hands: List[Hand] = []
    last_display: Optional[np.ndarray] = None
    frame_index = 0
    paused = False
    show_gesture_text = True
    show_hud = True
    show_bbox = bool(args.bbox)
    show_trail = bool(args.trail)
    custom_active = custom.enabled and not args.no_custom
    aspect = 3.0 / 4.0
    started = time.time()
    teach_done = 0
    last_teach = -6
    infer_ms = 0.0
    last_stats = time.time()

    if custom_active:
        log(f"[hand_landmarker] custom gestures: {', '.join(custom.labels)} ({gesture_path})")

    try:
        while True:
            if not paused:
                if stream is not None:
                    ok, frame = stream.read()
                else:
                    ok, frame = cap.read()
                if not ok or frame is None:
                    log("[hand_landmarker] end of stream")
                    break
                if mirror:
                    frame = cv2.flip(frame, 1)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                t_infer = time.perf_counter()
                hands = tracker.process(rgb)
                infer_ms = 0.9 * infer_ms + 0.1 * (time.perf_counter() - t_infer) * 1000.0

                now = time.perf_counter()
                fps_marks.append(now)
                while len(fps_marks) > 2 and now - fps_marks[0] > 1.0:
                    fps_marks.popleft()
                fps = ((len(fps_marks) - 1) / (fps_marks[-1] - fps_marks[0])
                       if len(fps_marks) > 2 and fps_marks[-1] > fps_marks[0] else 0.0)
                elapsed = time.time() - started
                aspect = _aspect_of(frame)
                h, w = frame.shape[:2]

                trail.clear()
                for hand in hands:
                    pts = smoother(hand.landmarks, now)
                    if pts is not None:
                        hand.landmarks = pts
                    raw, hand.pinch, hand.fingers = analyse(hand.landmarks, aspect)
                    if custom_active:
                        name, conf = custom.classify(
                            hand_features(hand.landmarks, hand.world, aspect))
                        if name:
                            raw, hand.custom_label, hand.custom_confidence = name, name, conf
                    hand.gesture = debouncer(raw)
                    trail.append(hand.px(8, w, h))
                    if arm is not None:
                        arm.update(hand)

                # ---- teach ------------------------------------------------
                if teaching and hands:
                    if args.teach_auto:
                        if teach_done < args.teach_auto and frame_index - last_teach >= 6:
                            custom.add(args.teach, hand_features(hands[0].landmarks,
                                                                 hands[0].world, aspect))
                            teach_done += 1
                            last_teach = frame_index
                            if teach_done >= args.teach_auto:
                                custom.save(gesture_path)
                                custom_active = True
                                log(f"[hand_landmarker] taught '{args.teach}' "
                                    f"with {teach_done} samples -> {gesture_path}")

                if csv_writer is not None:
                    for hand in hands:
                        flat = [round(float(v), 5) for v in hand.landmarks.reshape(-1)]
                        csv_writer.writerow([frame_index, round(elapsed, 4), hand.label,
                                             round(float(hand.score), 4), hand.gesture,
                                             round(hand.pinch, 4)] + flat)
                if args.json:
                    print(json.dumps({"frame": frame_index, "t": round(elapsed, 4),
                                      "hands": [hand_to_dict(h) for h in hands]}), flush=True)

                # ---- annotate (in place — no extra frame copy) -------------
                hud: List[str] = [f"{fps:5.1f} fps   {w}x{h}   frame {frame_index}",
                                  f"hands: {len(hands)}   backend: {tracker.backend}"
                                  + (f"/{tracker.delegate}" if tracker.backend == "tasks" else "")]
                hud += [_gesture_lines(hands, i) for i in range(len(hands))]
                if custom_active:
                    hud.append(f"custom: {len(custom.labels)} sign(s)")
                if teaching:
                    hud.append(f"teach {args.teach}: {custom.count(args.teach)} samples")
                annotate(hands, labels=show_gesture_text, indices=args.indices,
                         bbox=show_bbox, trail_pts=trail if show_trail else None,
                         hud=hud if show_hud else None, help_lines=show_window, frame=frame)
                last_display = frame
                frame_index += 1

                if writer is None and args.record and frame_index == 1:
                    src_fps = (args.cam_fps or 30.0) if kind == "camera" else cap.get(cv2.CAP_PROP_FPS)
                    out_fps = src_fps if 1 <= src_fps <= 120 else 30.0
                    writer = cv2.VideoWriter(args.record, cv2.VideoWriter_fourcc(*"mp4v"),
                                             out_fps, (w, h))
                    log(f"[hand_landmarker] recording -> {args.record} ({w}x{h} @ {out_fps:.0f} fps)")
                if writer is not None and last_display is not None:
                    writer.write(last_display)

                if args.stats and (now - last_stats > 2.0 or frame_index % 60 == 0):
                    last_stats = now
                    log(f"[stats] {fps:5.1f} fps | infer {infer_ms:5.1f} ms | "
                        f"total {1000.0 / max(fps, 1e-3):5.1f} ms"
                        + (f" | dropped {stream.dropped}" if stream is not None else ""))

            if last_display is not None and show_window:
                cv2.imshow("hand_landmarker", last_display)

            if show_window:
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
                if key == ord("m"):
                    mirror = not mirror
                    if arm is not None:
                        arm.mirror = mirror
                    log(f"[hand_landmarker] mirror {'on' if mirror else 'off'}")
                elif key == ord("t"):
                    if teaching:
                        if hands:
                            count = custom.add(args.teach, hand_features(
                                hands[0].landmarks, hands[0].world, aspect))
                            custom.save(gesture_path)
                            custom_active = True
                            log(f"[hand_landmarker] '{args.teach}': {count} samples")
                        else:
                            log("[hand_landmarker] no hand in frame — nothing recorded")
                    else:
                        log("[hand_landmarker] start with --teach NAME to record gestures")
                elif key == ord("c"):
                    custom_active = custom.enabled and not custom_active
                    debouncer.buf.clear()
                    log(f"[hand_landmarker] custom gestures {'on' if custom_active else 'off'}")
                elif key == ord("b"):
                    show_bbox = not show_bbox
                elif key == ord("k"):
                    show_trail = not show_trail
                elif key == ord("g"):
                    show_gesture_text = not show_gesture_text
                elif key == ord("h"):
                    show_hud = not show_hud
                elif key == ord("i"):
                    args.indices = not args.indices
                elif key == ord("s"):
                    if last_display is not None:
                        name = time.strftime("snapshot_%Y%m%d_%H%M%S.png")
                        cv2.imwrite(name, last_display)
                        log(f"[hand_landmarker] saved {name}")
                elif key == ord(" "):
                    paused = not paused
                    log("[hand_landmarker] paused" if paused else "[hand_landmarker] resumed")
            elif not args.json and frame_index and frame_index % 60 == 0:
                log(f"[hand_landmarker] {frame_index} frames, {fps:.1f} fps, "
                    f"{len(hands)} hand(s)")
    except KeyboardInterrupt:
        pass
    finally:
        if cap is not None:
            cap.release()
        if stream is not None:
            stream.release()
        if writer is not None:
            writer.release()
        if csv_file is not None:
            csv_file.close()
        if show_window:
            cv2.destroyAllWindows()
        tracker.close()
        if teaching and custom.count(args.teach):
            custom.save(gesture_path)
        if arm is not None:
            log(f"[arm] {arm.sent} command(s) sent")
            arm.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
