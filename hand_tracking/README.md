# hand_landmarker.py — the `hand_landmarker.task` demo, as one Python file

21 hand landmarks, handedness, gestures you can teach it, and optional control of
the robot arm — from a single `.py` file. No app, no browser, no server, nothing
uploaded anywhere. Your webcam frames never leave the machine.

```
hand_tracking/
├── hand_landmarker.py     ← the whole thing (one file), uses MediaPipe
├── hand_landmarker_cv.py  ← same output, no MediaPipe, OpenCV + NumPy only
├── requirements.txt
├── run_windows.bat        ← double-click: sets up a venv, installs, starts webcam
└── README.md
```

---

## What "replicate the .task file" can and can't mean — read this first

`hand_landmarker.task` is an ~8 MB **bundle of trained model weights**, not code.
Nobody re-creates the weights by rewriting them in Python, and anyone who says
otherwise is guessing. What *can* be reproduced in pure Python is everything the
bundle does:

| The `.task` demo gives you | This file gives you |
|---|---|
| 21 landmarks per hand, `x/y/z` normalised | ✅ same 21 points, same order |
| World landmarks in metres | ✅ same (both backends) |
| Left / right handedness + confidence | ✅ |
| Up to N hands | ✅ `--max-hands` |
| Runs from a file | ✅ `.py`, no build step |

**The trick that makes it "`.py` only":** the trained hand-landmark model is
already inside the `mediapipe` pip package (`mediapipe/modules/hand_landmark/`).
So `pip install mediapipe` + this file = working landmarks with **no `.task`
file to download at all**. That's the default backend.

| `--backend` | Model file | Notes |
|---|---|---|
| `solutions` | none — bundled in pip package | **default**, fully offline, tested |
| `tasks` | `hand_landmarker.task` | exact `.task` bundle; needs the file |
| `auto` | whichever is available | tries `.task` first, falls back |

---

## No MediaPipe at all: `hand_landmarker_cv.py`

`hand_landmarker.py` leans on MediaPipe's trained model. `hand_landmarker_cv.py`
does not: no `mediapipe`, no `.task`, no TFLite, no download — just geometry.

```
pip install opencv-python numpy
python hand_landmarker_cv.py --selftest         # every stage, no camera needed
python hand_landmarker_cv.py                    # webcam
python hand_landmarker_cv.py --calibrate        # learn the empty room first
python hand_landmarker_cv.py --image hand.jpg --out marked.jpg --json
```

It emits the **same 21 landmarks in the same order**, the same JSON fields
(`label`, `score`, `gesture`, `pinch`, `fingers`, `seen_tips`, `landmarks`,
`world_landmarks`), the same `--csv` / `--record` outputs and the same arm
protocol, so it drops into anything written for the other file. `world_landmarks`
is `null` because there is no depth (`z` is always `0`).

**How it works:** YCrCb skin mask → largest blob → palm circle from the distance
transform (ignores the forearm, which is thicker than the palm) → radial profile
→ fingertip peaks → sequence-align the peaks to the five fingers → interpolate
21 joints → gesture rules.

| | `hand_landmarker.py` | `hand_landmarker_cv.py` |
|---|---|---|
| Dependencies | `mediapipe opencv-python numpy` | `opencv-python numpy` |
| Model file | none (weights ship in the pip package) | none |
| Speed, CPU, 640×480 | ~27 fps (default mode) | ~77 fps (13 ms/frame) |
| Speed, CPU, 1280×720 | ~20 fps | ~31 fps (32 ms/frame) |
| Accuracy | 21 precise landmarks, any background | fingertips good, knuckles interpolated |
| Works on any background | yes | no — needs a non-skin background or `--calibrate` |
| Depth (`z`) | yes | no, always 0 |
| Fine poses (OK sign, 3 fingers) | yes | no |

**Windows notes.** If it dies with a one-line cv2 error (`int too big to
convert`, `Overload resolution failed`, a black window), run `--selftest` — it
prints your Python/NumPy/OpenCV versions and an ok/FAIL per stage, so you can
tell a code fault from a camera fault in one command. If the selftest passes but
the camera does not, try `--camera-backend dshow` or `--camera-backend msmf`,
and `--probe` to list working devices.

Measured on one machine, one photo set: open palm → `OPEN_PALM` with all five
fingertips on 240/240 frames of a synthetic video; closed fist → `FIST` on
120/120 frames. Where it breaks: a face in frame (skin too), a beige wall, a
hand with fingers pressed tightly together (reads as closed), and anything that
needs real joint angles.

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
without it. Cost: **free, forever** — open source libraries, Apache-2.0 model,
no account, no key, no quota.

---

## Run it

```bat
python hand_landmarker.py                        :: webcam, window, 2 hands
python hand_landmarker.py --fast                 :: lite model, 1 hand, 640x480
python hand_landmarker.py --max-hands 1
python hand_landmarker.py --probe                :: which camera indices work
python hand_landmarker.py --source clip.mp4      :: a video file
python hand_landmarker.py --image hand.jpg --out marked.jpg --json
python hand_landmarker.py --stats                :: capture / inference / fps numbers
```

### Keys in the preview window

| Key | Does |
|---|---|
| `q` / `Esc` | quit |
| `s` | save a PNG snapshot |
| `m` | mirror on/off |
| `b` | bounding box on/off |
| `k` | fingertip trail on/off |
| `t` | add a teaching sample (with `--teach NAME`) |
| `c` | custom gestures on/off |
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
 "hands": [{"label": "Right", "score": 0.97, "gesture": "OPEN_PALM",
            "gesture_source": "geometry", "gesture_confidence": 0.0, "pinch": 1.09,
            "fingers": {"thumb": true, "index": true, "middle": true, "ring": true, "pinky": true},
            "landmarks": [[0.43, 0.67, 0.0], "... 20 more ..."],
            "world_landmarks": [[-0.01, 0.08, 0.05], "... 20 more ..."]}]}
```

Landmark order is the standard MediaPipe one: `0` wrist, `1-4` thumb, `5-8`
index, `9-12` middle, `13-16` ring, `17-20` pinky.

---

## Gestures — built in

Geometry only, no extra model. Angles at the knuckles with the frame aspect
corrected, so it still works with the hand sideways or upside down. A 5-frame
majority vote (`--gesture-window`) stops flicker.

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
| `PINCH` | thumb + index touching, both reaching away | the `pinch` number |
| `OK` | pinch + middle/ring open | — |
| `NONE` | anything in between | — |

The continuous `pinch` value (0 ≈ touching, ~1.1 ≈ wide open) is usually more
useful than any label for driving a gripper.

---

## Teach it your own signs

The built-in set covers 10 poses. For anything else — a rock sign, a thumbs-up
variant, a sign that doesn't exist in any library — record a few examples and it
learns them on the spot. No training script, no TensorFlow, no GPU.

```bat
python hand_landmarker.py --teach ROCK --teach-auto 25   :: 25 samples, hands free
python hand_landmarker.py --teach ROCK                   :: press t ~25 times instead
python hand_landmarker.py --list-gestures                :: what's in gestures.json
python hand_landmarker.py --no-custom                    :: ignore the file
```

Samples are stored in `gestures.json` next to the script (about 700 bytes each,
git-ignored). Every later run picks it up automatically; when a taught sign wins,
`gesture` becomes its name and `gesture_source` becomes `"custom"`.

How it decides: every landmark is expressed in a **palm-aligned frame** — origin
at the wrist, x toward the index knuckle, z through the back of the hand, then
divided by palm length. That makes the numbers identical whether the hand is
upright, rotated, near, far, or pointing at the lens. A new frame is compared to
the stored examples; the 5 nearest vote; anything farther than `--custom-distance`
(0.35) is rejected and falls back to the built-in geometry.

| Knob | Default | Meaning |
|---|---|---|
| `--custom-k` | 5 | neighbours that vote |
| `--custom-threshold` | 0.55 | minimum share of the vote |
| `--custom-distance` | 0.35 | max distance; lower = stricter |

20–30 examples per sign is the sweet spot. Ten works for a clean, steady hand.

---

## What was borrowed from other projects (v1.1)

I read the popular MediaPipe hand projects on GitHub and took the parts that
actually help, rather than copying code:

| Project | What they do | What this file took |
|---|---|---|
| [Kazuhito00/hand-gesture-recognition-using-mediapipe](https://github.com/Kazuhito00/hand-gesture-recognition-using-mediapipe) (773★) | Log landmarks to CSV, train a small MLP in a notebook, load the `.tflite`; 16-frame `Counter` vote; fingertip trail; fps counter | Wrist-relative, scale-free features (plus a **rotation-normalised** palm frame they don't have), majority vote, trail, fps counter. **Skipped** the TensorFlow + notebook training step — nearest neighbour over the same features learns a sign in 25 frames, with zero extra dependencies |
| [cvzone/cvzone](https://github.com/cvzone/cvzone) (1.3k★) | `fingersUp()` via `tip.y < pip.y`; thumb by left/right x; bounding box + label | Bounding box and the fast `--bbox` / `--fast` ergonomics. **Did not** take the fingers-up test: it assumes an upright hand and breaks when you rotate your wrist |
| [google-ai-edge/mediapipe-samples](https://github.com/google-ai-edge/mediapipe-samples) (2.9k★) | Official `hand_landmarker` sample: plain `BaseOptions(model_asset_path=...)` in IMAGE mode | The Tasks API path, plus VIDEO mode and a `--delegate gpu` option they don't wire up |
| [PINTO0309/hand-gesture-recognition-using-onnx](https://github.com/PINTO0309/hand-gesture-recognition-using-onnx) (97★) | Replaces the whole MediaPipe graph with ONNX for speed | Nothing yet — it would add an export/build step and lose the "no model file" advantage. Worth revisiting only if CPU fps ever becomes the bottleneck |

Measured here (2-vCPU sandbox, 640×480 clip — expect better on a normal laptop):

| Build | Inference | End-to-end |
|---|---|---|
| v1.0, full model, 2 hands | 33–37 ms | ~27 fps |
| v1.1 `--fast` (lite model, 1 hand) | 8.6–8.8 ms | ~85 fps |
| v1.1 with `--smooth 0.5` vs `--smooth 0` | unchanged | 26.8 vs 26.1 fps |

Smoothing: on a synthetic 0.4 Hz sweep at 30 fps with 6 mm of noise, the One Euro
filter cut frame-to-frame jitter from 12.7 to 4.5–5.3 (2.5–2.8×) while keeping
RMS error at or below the raw signal, at about 1 frame of delay. A fixed-alpha
EMA can't do that — it needs one setting that is either jittery at rest or laggy
in motion.

Honest gap: the threaded camera reader cuts latency when inference is slower than
the camera, but this sandbox has no camera, so that one is reasoned, not measured.

---

## Robot arm (optional)

```bat
python hand_landmarker.py --dry-run                  :: print the commands, send nothing
python hand_landmarker.py --serial COM5 --baud 9600  :: actually send
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
   **one** device can hold an HC-05 at a time — close the phone app first.

Sanity-check the dry run before wiring anything: the numbers should move smoothly
from 0 to 300 as you sweep your hand across the camera.

---

## Tuning

| Symptom | Knob |
|---|---|
| Servo jitters | `--deadband 4 --send-hz 8 --smooth 0.7` |
| Arm lags behind the hand | `--smooth 0.3` |
| Low fps | `--fast`, or `--complexity 0 --max-hands 1 --width 640 --height 480` |
| Gestures flip too easily | `--gesture-window 9` |
| Taught sign fires for the wrong pose | lower `--custom-distance 0.25`, add more samples |
| Taught sign never fires | raise `--custom-distance 0.45`, or `--custom-threshold 0.4` |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `no matching distribution found for mediapipe` | Python 3.13+. Install 3.12 (`py -3.12 -m venv .venv`). |
| `could not open camera: 0` | `--probe` to list indices, then `--source 1`. Close Zoom/Teams/Camera first — Windows allows one app per camera. |
| `this OpenCV build has no GUI` | You have `opencv-python-headless`. `pip install opencv-python` (or keep `--no-window`). |
| Window is tiny/laggy | `--fast` |
| Model download fails (`--backend tasks`) | Download `hand_landmarker.task` in a browser, then `--model path\to\file.task`. Or don't — the default backend needs no file. |
| `--serial` fails: `PermissionError` | Port busy. Terminal app, phone app, or a previous run still holds it. |
| `W0000 ... inference_feedback_manager` on stderr | MediaPipe's own C++ log noise. Harmless; `--quiet` hides this script's messages, not those. |
| Landmark labels say `Left` for your right hand | MediaPipe assumes a mirrored (selfie) image. Mirroring is on by default; with `--no-mirror`, expect labels to swap. |

---

## How it works, in one paragraph

`HandTracker` wraps either `mediapipe.solutions.hands` (bundled model) or
`mediapipe.tasks.python.vision.HandLandmarker` (`.task` bundle) behind one
`process(rgb) -> [Hand]` call, so the rest of the program never cares which is
running. Each `Hand` carries the 21 × 3 landmarks, world landmarks, label, and
score. A threaded reader keeps only the newest camera frame; a One Euro filter
smooths landmarks without adding lag; `analyse()` turns geometry into a gesture
and a pinch ratio; `CustomGestures` compares palm-frame features against taught
examples; drawing is plain OpenCV; `ArmController` maps the result onto the arm's
ASCII protocol. Standard library plus mediapipe, OpenCV and NumPy — nothing else.
