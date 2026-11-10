# hand_landmarker.py — the `hand_landmarker.task` demo, as one Python file

21 hand landmarks, left/right handedness, gestures, and optional control of the
robot arm — from a single `.py` file. No app, no browser, no server, nothing
uploaded anywhere. Your webcam frames never leave the machine.

```
hand_tracking/
├── hand_landmarker.py     ← the whole thing (one file, ~950 lines)
├── requirements.txt
├── run_windows.bat        ← double-click: sets up a venv, installs, starts webcam
└── README.md
```

---

## What "replicate the .task file" can and can't mean — read this first

`hand_landmarker.task` is an ~8 MB **bundle of trained model weights**, not code.
Nobody can re-create the weights by rewriting them in Python, and anyone who says
otherwise is guessing. What *can* be reproduced in pure Python is everything the
bundle does:

| The `.task` demo gives you | This file gives you |
|---|---|
| 21 landmarks per hand, `x/y/z` normalised | ✅ same 21 points, same order |
| World landmarks in metres | ✅ same (solutions + tasks backends) |
| Left / right handedness + confidence | ✅ |
| Up to N hands | ✅ `--max-hands` |
| Runs from a file | ✅ `.py`, no build step |

**The trick that makes it "`.py` only":** the trained hand-landmark model is
already inside the `mediapipe` pip package (`mediapipe/modules/hand_landmark/`).
So `pip install mediapipe` + this file = working landmarks with **no `.task`
file to download at all**. That's the default backend.

If you *want* the exact same bundle path, the script also speaks the Tasks API —
drop `hand_landmarker.task` next to the script (or pass `--model`), and it uses
it. It will even fetch the official file from Google once if you ask for it.

| `--backend` | Model file | Notes |
|---|---|---|
| `solutions` | none — bundled in pip package | **default**, fully offline, tested |
| `tasks` | `hand_landmarker.task` | exact `.task` bundle; needs the file |
| `auto` | whichever is available | tries `.task` first, falls back |

---

## Install

Needs **Python 3.9 – 3.12** (MediaPipe has no 3.13 wheels yet — if `pip` says
"no matching distribution", that's why).

**Windows (easiest):** double-click `run_windows.bat`. First run installs
everything into `.venv` (about 90 MB, once), then opens the camera.

**Manual, any OS:**

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python hand_landmarker.py
```

macOS / Linux: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`

`pyserial` is only needed for the robot arm (`--serial`). Everything else works
without it.

Cost: **free, forever.** All libraries are open source, the model is Apache-2.0,
and there is no account, key, or quota.

---

## Run it

```bat
python hand_landmarker.py                        :: webcam, window, 2 hands
python hand_landmarker.py --max-hands 1          :: one hand, a bit faster
python hand_landmarker.py --complexity 0         :: lite model, higher fps
python hand_landmarker.py --probe                :: which camera indices work
python hand_landmarker.py --source clip.mp4      :: a video file
python hand_landmarker.py --image hand.jpg --out marked.jpg --json
```

### Keys in the preview window

| Key | Does |
|---|---|
| `q` / `Esc` | quit |
| `s` | save a PNG snapshot |
| `m` | mirror on/off |
| `g` | hide/show gesture text |
| `h` | hide/show the stats panel |
| `i` | show landmark indices `0-20` |
| `space` | pause / resume |

### Output you can pipe somewhere

| Flag | Output |
|---|---|
| `--json` | one JSON object per frame on stdout |
| `--csv log.csv` | every landmark, every frame, appended to a CSV |
| `--out marked.jpg` | annotated still (image mode) |
| `--record out.mp4` | annotated video with the skeleton burned in |

`--json` line shape:

```json
{"frame": 42, "t": 1.4,
 "hands": [{"label": "Right", "score": 0.97, "gesture": "OPEN_PALM", "pinch": 1.09,
            "fingers": {"thumb": true, "index": true, "middle": true, "ring": true, "pinky": true},
            "landmarks": [[0.43, 0.67, 0.0], "... 20 more ..."],
            "world_landmarks": [[-0.01, 0.08, 0.05], "... 20 more ..."]}]}
```

Landmark order is the standard MediaPipe one: `0` wrist, `1-4` thumb, `5-8`
index, `9-12` middle, `13-16` ring, `17-20` pinky.

---

## Gestures

Geometry only — no extra model, no training. Angles at the knuckles, so they
still work with the hand sideways or upside down. A 5-frame majority vote
(`--gesture-window`) stops the label flickering.

| Gesture | How | Used for |
|---|---|---|
| `OPEN_PALM` | all five extended | light: normal |
| `FIST` | all curled | **freeze the arm** |
| `POINT` | index only | — |
| `PEACE` | index + middle | light: normal |
| `THREE` / `FOUR` | 3 / 4 fingers, thumb tucked | — |
| `GUN` | index + middle + thumb | — |
| `THUMBS_UP` | fist, thumb pointing up | light: warm |
| `THUMBS_DOWN` | fist, thumb pointing down | light: cool |
| `PINCH` | thumb + index touching, both reaching away | reported as `pinch` |
| `OK` | pinch + middle/ring open | — |
| `NONE` | anything in between | — |

The continuous `pinch` number (0 ≈ touching, ~1.1 ≈ wide open) is usually more
useful than the label for driving a gripper.

---

## Robot arm (optional)

```bat
python hand_landmarker.py --dry-run                  :: print the commands, send nothing
python hand_landmarker.py --serial COM5 --baud 9600  :: actually send
python hand_landmarker.py --serial COM5 --baud 9600 --no-mirror
```

Mapping, applied at `--send-hz` (12/s) with a `--deadband` of 2° so a shaky hand
doesn't spam the link:

| Hand | Command | Range |
|---|---|---|
| wrist left ↔ right | `B<0-300>#` | full base travel |
| wrist high ↔ low | `E<30-150>#` | elbow |
| thumb–index pinch | `H<45-135>#` | fingers together = closed |
| 👍 / 👎 / ✌ | `TW#` / `TC#` / `TN#` | light, sent once per change |
| ✊ fist | *(nothing)* | arm holds position |
| no hand in frame | *(nothing)* | arm holds position |

**Two catches, stated up front:**

1. **Your Mega firmware only knows `B` and `S` right now** (`servo_test_vscode/`
   ignores `H`, `E`, `TW`, `TN`, `TC`, `M`, `P`). So today this moves the **base
   only**. The other commands are already correct — they start working when the
   firmware grows head + elbow + light.
2. **The laptop must own the Bluetooth link.** Pair the HC-05 *from the laptop*,
   let Windows create an outgoing COM port (`COM5` or similar), and remember only
   **one** device can hold an HC-05 at a time — close the phone app first. The
   phone app and this script can't drive the arm simultaneously.

Sanity-check the dry run before wiring anything: the numbers should move smoothly
from 0 to 300 as you sweep your hand across the camera.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `no matching distribution found for mediapipe` | Python 3.13+. Install 3.12 (`py -3.12 -m venv .venv`). |
| `could not open camera: 0` | `--probe` to list indices, then `--source 1`. Close Zoom/Teams/Camera first — Windows allows one app per camera. |
| `this OpenCV build has no GUI` | You have `opencv-python-headless`. `pip install opencv-python` (or keep `--no-window`). |
| Window is tiny/laggy | `--complexity 0 --width 640 --height 480` |
| Model download fails (`--backend tasks`) | Download `hand_landmarker.task` in a browser, then `--model path\to\file.task`. Or just don't — the default backend needs no file. |
| `--serial` fails: `PermissionError` | Port busy. Terminal app, phone app, or a previous run still holds it. |
| Servo jitters | Raise `--deadband 4`, lower `--send-hz 8`, add `--smooth 0.7`. |
| `W0000 ... inference_feedback_manager` on stderr | MediaPipe's own C++ log noise. Harmless; `--quiet` hides this script's messages, not those. |
| Landmark labels say `Left` for your right hand | MediaPipe assumes a mirrored (selfie) image. Mirroring is on by default; with `--no-mirror`, expect labels to swap. |

---

## How it works, in one paragraph

`HandTracker` wraps either `mediapipe.solutions.hands` (bundled model) or
`mediapipe.tasks.python.vision.HandLandmarker` (`.task` bundle) behind one
`process(rgb) -> [Hand]` call, so the rest of the program never cares which is
running. Each `Hand` carries the 21 × 3 landmarks, world landmarks, label, and
score. `analyse()` turns the geometry into a gesture and a pinch ratio; drawing is
plain OpenCV; `ArmController` maps the result onto the arm's ASCII protocol. That's
the whole pipeline — about 950 lines, standard library plus mediapipe, OpenCV and
NumPy.
