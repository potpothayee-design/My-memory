#!/usr/bin/env python3
"""
hand_landmarker.py — one-file, pure-Python hand landmarker.

Replicates what MediaPipe's `hand_landmarker.task` bundle does — 21 3-D hand
landmarks, left/right handedness, per-hand score — from a single .py file.

Two backends, both inside the `mediapipe` wheel:

  solutions  (default)  mediapipe.solutions.hands. The trained hand-landmark
                        model ships inside the pip package, so there is NO
                        .task file to download and no extra asset at all.
  tasks                 mediapipe.tasks.python.vision.HandLandmarker, i.e. the
                        exact .task bundle path. Used automatically when a
                        hand_landmarker.task file is present, or downloaded
                        when you pass --backend tasks (needs internet once).

The model itself (millions of trained weights) cannot be reproduced by
rewriting code — what this file reproduces is the API and the output: the same
21 landmarks, same order, same normalised coordinates.

Quick start
-----------
    pip install -r requirements.txt
    python hand_landmarker.py                  # webcam, window
    python hand_landmarker.py --source photo.jpg --out marked.jpg --json
    python hand_landmarker.py --dry-run         # see the arm commands

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
import time
import urllib.request
from collections import deque
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

# Silence MediaPipe / TensorFlow C++ chatter before importing them.
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import numpy as np  # noqa: E402

try:
    import cv2  # noqa: E402
except ImportError:  # pragma: no cover - guidance only
    sys.exit("OpenCV is missing. Run:  pip install opencv-python")

QUIET = False


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
C_DARK = (20, 20, 20)
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

    def px(self, index: int, width: int, height: int) -> Tuple[int, int]:
        x, y = self.landmarks[index][:2]
        return int(round(float(x) * width)), int(round(float(y) * height))


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
    sideways or upside down. Coordinates are scaled by the frame aspect ratio
    first, otherwise a wide webcam frame would squash the geometry.
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
# Backends
# --------------------------------------------------------------------------- #

class HandTracker:
    """Uniform wrapper over mediapipe's solutions and tasks APIs."""

    def __init__(self, backend: str = "auto", model_path: Optional[str] = None,
                 max_hands: int = 2, min_detection: float = 0.5,
                 min_tracking: float = 0.5, complexity: int = 1,
                 streaming: bool = True, allow_download: bool = True) -> None:
        self.max_hands = max(1, int(max_hands))
        self.streaming = streaming
        self.backend = self._choose(backend, model_path, allow_download)
        self._ts = 0
        self._last_ts = 0

        if self.backend == "tasks":
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision

            opts = vision.HandLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=self.model_path),
                running_mode=vision.RunningMode.VIDEO if streaming else vision.RunningMode.IMAGE,
                num_hands=self.max_hands,
                min_hand_detection_confidence=float(min_detection),
                min_hand_presence_confidence=float(min_detection),
                min_tracking_confidence=float(min_tracking),
            )
            self._lm = vision.HandLandmarker.create_from_options(opts)
            self._mp_image = None
        else:
            import mediapipe as mp

            self._hands = mp.solutions.hands.Hands(
                static_image_mode=not streaming,
                max_num_hands=self.max_hands,
                model_complexity=int(complexity),
                min_detection_confidence=float(min_detection),
                min_tracking_confidence=float(min_tracking),
            )
        log(f"[hand_landmarker] backend={self.backend}"
            + (f" model={self.model_path}" if self.backend == "tasks" else " (model bundled in mediapipe)"))

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
        except Exception:                            # noqa: BLE001 - best effort
            pass


# --------------------------------------------------------------------------- #
# Temporal smoothing
# --------------------------------------------------------------------------- #

class OneEuro:
    """Tiny exponential smoother for landmark sequences.

    alpha is frame-rate independent-ish: higher = snappier, more jitter;
    lower = calmer, more lag. 0 disables smoothing.
    """

    def __init__(self, alpha: float = 0.55) -> None:
        self.alpha = float(alpha)
        self.state: Optional[np.ndarray] = None

    def __call__(self, points: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if points is None or self.alpha <= 0:
            self.state = points
            return points
        if self.state is None or self.state.shape != points.shape:
            self.state = points.copy()
        else:
            self.state = self.alpha * points + (1.0 - self.alpha) * self.state
        return self.state


class GestureDebouncer:
    """Majority vote over the last `window` frames — kills one-frame flicker."""

    def __init__(self, window: int = 5) -> None:
        self.buf: deque = deque(maxlen=max(1, int(window)))
        self.current = "NONE"

    def __call__(self, gesture: Optional[str]) -> str:
        if gesture is None:
            self.buf.clear()
            self.current = "NONE"
            return self.current
        self.buf.append(gesture)
        if self.buf:
            counts: dict = {}
            for g in self.buf:
                counts[g] = counts.get(g, 0) + 1
            best = max(counts, key=counts.get)
            if counts[best] * 2 >= len(self.buf):
                self.current = best
        return self.current


# --------------------------------------------------------------------------- #
# Drawing
# --------------------------------------------------------------------------- #

def _line_thickness(height: int) -> int:
    return max(1, int(round(height / 320)))


def draw_hand(frame: np.ndarray, hand: Hand, *, show_points: bool = True,
              show_labels: bool = True, show_indices: bool = False) -> None:
    h, w = frame.shape[:2]
    thick = _line_thickness(h)
    r = max(2, int(round(min(w, h) * 0.007)))

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
        for i in range(21):
            x, y = hand.px(i, w, h)
            cv2.putText(frame, str(i), (x + r + 2, y - r), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35 * max(0.8, min(w, h) / 720), C_DARK, 2, cv2.LINE_AA)
            cv2.putText(frame, str(i), (x + r + 2, y - r), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35 * max(0.8, min(w, h) / 720), C_TEXT, 1, cv2.LINE_AA)

    if show_labels:
        x, y = hand.px(0, w, h)
        text = f"{hand.label} {hand.score:.2f}" if hand.label != "?" else f"{hand.score:.2f}"
        _text(frame, text, (x + int(min(w, h) * 0.03), y + int(min(w, h) * 0.05)),
              max(0.45, min(w, h) / 900), C_ACCENT, 2)


def _text(frame: np.ndarray, text: str, org: Tuple[int, int], scale: float,
          color: Tuple[int, int, int] = C_TEXT, thick: int = 1) -> None:
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, C_DARK,
                thick + 2, cv2.LINE_AA)
    cv2.putText(frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                thick, cv2.LINE_AA)


def draw_hud(frame: np.ndarray, *, fps: float, backend: str, hands: Sequence[Hand],
             show_help: bool, send_hz: Optional[float] = None) -> None:
    h, w = frame.shape[:2]
    scale = max(0.38, min(0.75, min(w, h) / 900))
    head = f"{fps:5.1f} fps" if fps > 0 else "single image"
    lines = [head, f"hands: {len(hands)}", f"backend: {backend}"]
    for i, hand in enumerate(hands):
        lines.append(f"H{i + 1} {hand.label:<5} {hand.gesture:<11} pinch {hand.pinch:.2f}")
    if send_hz is not None:
        lines.append(f"arm link {send_hz:.0f} Hz")

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
            "q quit   s snapshot   m mirror   g gestures",
            "i indices   h hud   space pause",
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
            # Dry run: the commands are the output, so they go to stdout even with --quiet.
            print(f"[arm] -> {command}", flush=True)

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
        "pinch": round(float(hand.pinch), 4),
        "fingers": dict(zip(FINGER_NAMES, (bool(f) for f in hand.fingers))),
        "landmarks": [[round(float(v), digits) for v in row] for row in hand.landmarks],
        "world_landmarks": ([[round(float(v), digits) for v in row] for row in hand.world]
                            if hand.world is not None else None),
    }


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hand_landmarker.py",
        description="Pure-Python hand landmarker (21 points) and gesture/robot-arm bridge.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples\n"
            "  python hand_landmarker.py\n"
            "  python hand_landmarker.py --source 1 --max-hands 1\n"
            "  python hand_landmarker.py --source hand.jpg --out marked.jpg --json\n"
            "  python hand_landmarker.py --serial COM5 --baud 9600\n"
            "  python hand_landmarker.py --dry-run                  # print arm commands, no serial\n"
            "  python hand_landmarker.py --probe                    # list working cameras\n"
        ),
    )
    p.add_argument("--source", default=None,
                   help="camera index (0, 1, ...), video path, or image path. Default: 0")
    p.add_argument("--camera", type=int, default=None, help="shorthand for --source N")
    p.add_argument("--image", default=None, help="shorthand: process a single image")
    p.add_argument("--video", default=None, help="shorthand: process a video file")
    p.add_argument("--width", type=int, default=1280, help="camera capture width (default 1280)")
    p.add_argument("--height", type=int, default=720, help="camera capture height (default 720)")
    p.add_argument("--max-hands", type=int, default=2, help="hands to track, 1-4 (default 2)")

    g = p.add_argument_group("model")
    g.add_argument("--backend", choices=("auto", "solutions", "tasks"), default="auto",
                   help="solutions = bundled model, no .task file (default auto)")
    g.add_argument("--model", default=None,
                   help=f"path to hand_landmarker.task (default: ./{DEFAULT_MODEL_NAME})")
    g.add_argument("--no-download", action="store_true", help="never fetch the .task file")
    g.add_argument("--complexity", type=int, choices=(0, 1), default=1,
                   help="solutions model: 0 = lite/fast, 1 = full/accurate (default 1)")
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
    o.add_argument("--smooth", type=float, default=0.55,
                   help="landmark smoothing 0..1, 0 = off (default 0.55)")
    o.add_argument("--gesture-window", type=int, default=5,
                   help="frames of majority vote for gestures (default 5)")
    o.add_argument("--quiet", action="store_true", help="suppress diagnostics on stderr")

    a = p.add_argument_group("robot arm (HC-05)")
    a.add_argument("--serial", default=None, help="serial port, e.g. COM5 or /dev/rfcomm0")
    a.add_argument("--baud", type=int, default=9600, help="HC-05 baud (default 9600)")
    a.add_argument("--send-hz", type=float, default=12.0, help="max commands per second (12)")
    a.add_argument("--deadband", type=int, default=2, help="min angle change to send (2)")
    a.add_argument("--dry-run", action="store_true", help="print arm commands, send nothing")

    m = p.add_argument_group("misc")
    m.add_argument("--probe", action="store_true", help="list working camera indices and exit")
    m.add_argument("--version", action="version", version="hand_landmarker.py 1.0")
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

    streaming = kind != "image"
    mirror = (not args.no_mirror) if kind == "camera" else False
    show_window = args.show or (not args.no_window and kind == "camera")

    if show_window and not hasattr(cv2, "imshow"):
        log("[hand_landmarker] this OpenCV build has no GUI (headless). "
            "Install 'opencv-python', or run with --no-window.")
        show_window = False

    tracker = HandTracker(
        backend=args.backend,
        model_path=args.model,
        max_hands=args.max_hands,
        min_detection=args.min_detection,
        min_tracking=args.min_tracking,
        complexity=args.complexity,
        streaming=streaming,
        allow_download=not args.no_download,
    )

    smoother = OneEuro(args.smooth)
    debouncer = GestureDebouncer(args.gesture_window)

    arm: Optional[ArmController] = None
    use_arm = bool(args.serial or args.dry_run)
    if use_arm:
        arm = ArmController(port=args.serial, baud=args.baud, dry_run=args.dry_run,
                            hz=args.send_hz, mirror=mirror, deadband=args.deadband)

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

    # ---- single image ------------------------------------------------------ #
    if kind == "image":
        frame = cv2.imread(str(value))
        if frame is None:
            raise SystemExit(f"could not read image: {value}")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hands = tracker.process(rgb)
        aspect = _aspect_of(frame)
        for hand in hands:
            pts = smoother(hand.landmarks)
            if pts is not None:
                hand.landmarks = pts
            hand.gesture, hand.pinch, hand.fingers = analyse(hand.landmarks, aspect)
            if arm is not None:
                arm.update(hand)

        annotated = frame.copy()
        for hand in hands:
            draw_hand(annotated, hand, show_indices=args.indices)
        draw_hud(annotated, fps=0.0, backend=tracker.backend, hands=hands, show_help=False)

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
    cap = cv2.VideoCapture(int(value) if kind == "camera" else str(value))
    if not cap.isOpened():
        raise SystemExit(f"could not open {kind}: {value}"
                         + ("  (try --probe)" if kind == "camera" else ""))
    if kind == "camera":
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    writer = None
    if args.record:
        src_fps = cap.get(cv2.CAP_PROP_FPS)
        fps_out = src_fps if 1 <= src_fps <= 120 else 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or args.width
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or args.height
        writer = cv2.VideoWriter(args.record, cv2.VideoWriter_fourcc(*"mp4v"), fps_out, (w, h))
        log(f"[hand_landmarker] recording -> {args.record} ({w}x{h} @ {fps_out:.0f} fps)")

    fps = 0.0
    frame_index = 0
    paused = False
    show_gesture = True
    show_hud = True
    last_frame = None
    hands: List[Hand] = []
    started = time.time()

    try:
        while True:
            if not paused:
                ok, frame = cap.read()
                if not ok or frame is None:
                    log("[hand_landmarker] end of stream")
                    break
                if mirror:
                    frame = cv2.flip(frame, 1)

                t0 = time.perf_counter()
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                hands = tracker.process(rgb)
                dt = max(time.perf_counter() - t0, 1e-6)
                fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps else 1.0 / dt
                elapsed = time.time() - started

                aspect = _aspect_of(frame)
                for hand in hands:
                    pts = smoother(hand.landmarks)
                    if pts is not None:
                        hand.landmarks = pts
                    raw_gesture, hand.pinch, hand.fingers = analyse(hand.landmarks, aspect)
                    hand.gesture = debouncer(raw_gesture) if show_gesture else raw_gesture
                    if arm is not None:
                        arm.update(hand)

                if csv_writer is not None:
                    for hand in hands:
                        flat = [round(float(v), 5) for v in hand.landmarks.reshape(-1)]
                        csv_writer.writerow([frame_index, round(elapsed, 4), hand.label,
                                             hand.score, hand.gesture, round(hand.pinch, 4)]
                                            + flat)
                if args.json:
                    print(json.dumps({"frame": frame_index, "t": round(elapsed, 4),
                                      "hands": [hand_to_dict(h) for h in hands]}), flush=True)

                last_frame = frame
                frame_index += 1

            if last_frame is not None:
                display = last_frame.copy()
                for hand in hands:
                    draw_pinch_bar(display, hand)
                for hand in hands:
                    draw_hand(display, hand, show_labels=show_gesture, show_indices=args.indices)
                if show_hud:
                    draw_hud(display, fps=fps, backend=tracker.backend, hands=hands,
                             show_help=show_window,
                             send_hz=args.send_hz if arm is not None else None)

                if writer is not None:
                    writer.write(display)
                if show_window:
                    cv2.imshow("hand_landmarker", display)

            if show_window:
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
                if key == ord("m"):
                    mirror = not mirror
                    if arm is not None:
                        arm.mirror = mirror
                    log(f"[hand_landmarker] mirror {'on' if mirror else 'off'}")
                elif key == ord("g"):
                    show_gesture = not show_gesture
                    debouncer.buf.clear()
                elif key == ord("h"):
                    show_hud = not show_hud
                elif key == ord("i"):
                    args.indices = not args.indices
                elif key == ord("s"):
                    if last_frame is not None:
                        name = time.strftime("snapshot_%Y%m%d_%H%M%S.png")
                        cv2.imwrite(name, display)
                        log(f"[hand_landmarker] saved {name}")
                elif key == ord(" "):
                    paused = not paused
                    log("[hand_landmarker] paused" if paused else "[hand_landmarker] resumed")
            elif not args.json and frame_index % 60 == 0:
                # Headless run: one progress line every ~2 s (not per frame).
                log(f"[hand_landmarker] {frame_index} frames, {fps:.1f} fps, "
                    f"{len(hands)} hand(s)")
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
        tracker.close()
        if arm is not None:
            log(f"[arm] {arm.sent} command(s) sent")
            arm.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
