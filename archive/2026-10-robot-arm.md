# Robot arm — Arduino Mega 2560 + HC-05 (classic Bluetooth)

**Cold layer.** Fetched only when the topic is the robot arm, Bluetooth, HC-05, Arduino, servos,
the `.aia` apps, or PlatformIO. Not loaded by default.

**Last updated:** 2026-10-05

> **Correction, 2026-10-05 — the old "BLE" framing was wrong.** An earlier version of this file said
> "Classic Bluetooth — does NOT work with my module" and named `final_sure_part_1_ble.aia` as the
> main app. Both were backwards. The module is an **HC-05: classic Bluetooth only**. It pairs, sits
> under *Bluetooth Classic* in the phone's device list, and works over classic SPP at **9600 baud**
> (verified: a terminal app round-trips `S0#` → `OK 0`). A BLE scan cannot discover it, so the
> BluetoothLE-extension build (`finalble.aia`) can never connect. **That — not a wiring fault — is
> why the app could not move the servo.** Use the classic build.

---

## What it is

A robot arm — head, elbow, base, plus a light — driven by an **Arduino Mega 2560** and controlled
from an **Android app over classic Bluetooth** (MIT App Inventor).

## Files — as they actually exist in the repo

| File | What it is |
|---|---|
| `eto ns tslaga.aia` | **Use this one.** Newest classic build (`BluetoothClient1`), QR scanner + duplicate connect button already stripped, hold/repeat clocks wired. Patched 2026-10-05 (list below) |
| `finalble.aia` | The *same app*, transport swapped to `BluetoothLE1` (MIT BLE extension, FFE0/FFE1). **Cannot connect to an HC-05** |
| `final_sure_part_1.aia` | Oldest classic build, still has the QR scanner. Superseded by `eto ns tslaga.aia` |
| `servo_test_vscode/` | PlatformIO project for the Mega. Base-joint-only test firmware, added 2026-10-05 |

Older notes named `final_sure_part_1_ble.aia` and `BLE_Test.aia` as the main and test apps. Neither
was ever in the repo; `finalble.aia` is the BLE build that does exist.

## Hardware

| Part | Mega pin |
|---|---|
| HC-05 VCC / GND | 5V / GND |
| HC-05 **TXD** | **19 (RX1)** |
| HC-05 **RXD** | **18 (TX1)** — voltage divider recommended |
| **Base servo signal** | **9** |
| Servo red / brown | 5V / GND — external 5V better, shared GND |

- Module: **HC-05**, MAC `E1:4E:2F:5D:3A:A2`, paired, **9600 baud**, appears under *Bluetooth
  Classic*.
- **Base servo: 300°**, on pin 9.
- Head / elbow servos: standard 180° class, pins not recorded yet.
- The Mega uses **Serial1** — not SoftwareSerial (**pin 2 cannot receive on a Mega**).
- On the Mega the Servo library uses **Timer5** → **no PWM on pins 44, 45, 46**. Use 2–8 for LED PWM.

## Servo-library gotchas that cost time

- **`servo.write(300)` does nothing past 180.** `write()` accepts 0–180 only. Symptom, straight from
  the terminal log: `S300#` → `OK 180`, so the base never used most of its travel. For the 300° base
  use **`writeMicroseconds()`** with a mapped range and `attach(pin, min, max)`.
- **Do not "fix" it with `servo.write(2500)`.** On AVR any value **≥ 544** passed to `write()` is
  reinterpreted as a **pulse width in microseconds** — so `S600#` would jump to ~600 µs.
- **Non-servo commands must be filtered.** The first diagnostic parsed `cmd.substring(1).toInt()`
  for *every* command, so `TW#` snapped the servo to 0°, `M1#` to 1°, `P50#` to 50°.
- Calibrating `MIN_US` / `MAX_US` for the base is still open (see BRAIN §7).

## Commands the app sends

All end with `#`; the firmware also ignores `\r` / `\n`.

| Command | Meaning |
|---|---|
| `H<angle>#` | Head (45–135) |
| `E<angle>#` | Elbow (30–150) |
| `B<angle>#` | Base (0–300 in both app and firmware as of 2026-10-05) |
| `B175#E90#H90#` | Reset position — sent as **one** string, so a base-only firmware sees `B175#` and logs the rest |
| `TW#` / `TN#` / `TC#` | Warm / Normal / Cool light |
| `P<0-100>#` | Brightness |
| `M1#` / `M0#` | Gesture / Mobile mode |
| `S<angle>#` | Servo test (test firmware only) |

The app sends these with `BluetoothClient.SendText`. Every payload in the BLE build was verified
plain ASCII with `utf16 = FALSE`; the classic build sends the same strings.

## App fixes made — all in `eto ns tslaga.aia`

Earlier round: Bluetooth permission requests (Android 12+: `BLUETOOTH_CONNECT` / `BLUETOOTH_SCAN`;
location for older versions); hold-to-repeat buttons actually enabled (`HoldClock` / `RepeatClock`
were never switched on and `TouchUp` was empty); `RepeatClock` used `<` instead of `=` — fixed;
brightness slider only sends on change; QR scanner and duplicate connect button removed.

2026-10-05: `ErrorOccurred` no longer swallows **error 507** ("Unable to connect — is the device
turned on?"), so a failed connect is visible instead of silent; `lastBrightness` resets to -1 on
connect; the gesture-mode banner no longer claims camera input is active; **base ceiling lowered
350 → 300** to match the servo (the 350 ceiling meant the last 50° of tapping sent commands that the
firmware clamped, so the arm sat still while the app looked broken).

## Known defects / still open

- **Gesture mode is a stub.** Tapping it flips the toggle, sends `M1#`, locks every manual control
  and shows a banner — but there is **no Camera component and no gesture blocks**. Nothing drives
  the arm in that mode. It's "Part 2".
- **`longPressActive` is never cleared on `TouchUp`.** Press, hold, slide your finger off the
  button, release → `TouchUp` fires but `Click` doesn't, so the flag stays `TRUE` and the *next*
  quick tap is swallowed. One dead tap after every dragged-off press.
- **Holding is slower than tapping:** tap = 5°, hold = 1° per 100 ms after a 400 ms delay.
- `finalble.aia` never got the 2026-10-05 fixes (its banner still claims camera input). Only
  matters if the module is ever swapped for a real BLE one.

## Firmware — `servo_test_vscode/`

PlatformIO, `board = megaatmega2560`, `monitor_speed = 9600`. Deliberately **base-joint only**: get
one axis moving end to end before wiring the rest. Accepts `B<angle>#` and `S<angle>#`; ignores
`H` / `E` / `TW` / `TN` / `TC` / `M` / `P` instead of parsing them as angles. Prints every byte from
the module as `BLE raw:` with a running count.

Reading the Serial Monitor:

| What you see | Meaning |
|---|---|
| clean characters (`BLE raw: 'B' (66)`) | data arriving — the base should move |
| `255` / `254` garbage | **baud mismatch** — try 38400, then 115200 |
| nothing at all | not connected, module stuck in AT mode (slow blink), or another app holds the link |

## Tools / setup

- VS Code + **PlatformIO IDE** extension. The C/C++ extension pack isn't needed.
- Open the folder that **contains** `platformio.ini` directly, or includes show red errors.
- Bottom bar: Build, Upload, Serial Monitor (**9600 baud**).
- **Only one device can connect to the HC-05 at a time** — close the Bluetooth terminal app before
  the phone app tries to connect.
- The Module's own UART baud (AT+BAUD) and the sketch's `ble.begin(...)` must match. 9600 is
  confirmed working.

## Next steps

1. Flash `servo_test_vscode/`, connect with `eto ns tslaga.aia`, get the **base** moving.
2. Calibrate `MIN_US` / `MAX_US` for the 300° base and narrow the app's base range if the joint
   hits a mechanical stop early.
3. Extend the firmware to head + elbow + light (all four axes).
4. Test the full app against the full firmware.
5. Part 2: gesture mode — **undefined so far.** No camera component exists; decide what "gesture"
   means before building it.
6. _(The original source list ended mid-item — the last step was never written down. Ask, don't
   guess.)_
