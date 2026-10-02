# Robot arm / Geslamp — Arduino Mega (2026-10)

**Cold layer.** Fetched only when the topic is Geslamp, the robot arm, BLE, HC-05, Arduino, servos,
the `.aia` apps, or PlatformIO. Not loaded by default.

**Last updated:** 2026-10-02

---

## What it is

**Geslamp** — head, elbow, base, plus a light — driven by an **Arduino Mega 2560** and an
**Android MIT App Inventor** app.

## Radio — UNSETTLED

| Claim | Source |
|---|---|
| Module is **BLE**; classic Bluetooth does **not** work | Prior brain (2026-10-02 rebuild) |
| **HC-05 classic SPP** works: Serial Bluetooth Terminal **moves the servo**; the App Inventor app did not | Session 2026-10-02 |

Do not assume BLE or HC-05. If it matters, ask. Work in the later session is **HC-05**.

PIN for pairing: **1234 or 0000**. **Only one client at a time** — close Serial Bluetooth Terminal
before the app connects.

## Files

| File | What it is |
|---|---|
| `final_sure_part_1.aia` | UI they want: QR scan + manual HC-05 picker, Gesture/Mobile, Head/Elbow/Base, light, brightness. Classic BluetoothClient. |
| `eto ns tslaga.aia` | Earlier classic-BT Geslamp (no QR) |
| `Geslamp-with-connection.aia` | **Use this:** their UI + address-based HC-05 connect (see below) |
| `final_sure_part_1_ble.aia` | Earlier BLE conversion (not in this repo snapshot; cited by prior brain) |
| `BLE_Test.aia` | Small BLE test app (cited by prior brain; not in this snapshot) |
| `servo_test_vscode/` | PlatformIO Mega diagnostic (cited by prior brain; not in this snapshot) |

## How they want to connect (classic BT)

**By Bluetooth MAC address**, not by name alone.

- List picker uses `BluetoothClient.AddressesAndNames` (`AA:BB:CC:DD:EE:FF HC-05`).
- App takes the **first token** (the MAC) and connects SPP UUID `00001101-0000-1000-8000-00805F9B34FB`, **insecure first**.
- Manual **CONNECT** uses that same picked address.
- **QR is optional.** The code should be the MAC (e.g. `00:11:22:33:44:55`).

Prefer **Build APK** over MIT Companion on Android 12+.

## Why the original app didn't move servos (terminal did)

Hardware + Arduino protocol were fine. App issues:

- `SendText` sent `H90#` with **no CR/LF**; terminals append `\r\n`.
- Tried **secure** RFCOMM first; HC-05 usually needs **insecure** SPP.
- After connect, did **not** send `M1#` (Mobile Mode) — firmware may ignore servo cmds in gesture mode.
- App Inventor can stringify angles as `H90.0#` instead of `H90#`.
- Buttons **silently did nothing** when not connected.
- Android 12+ needs `BLUETOOTH_CONNECT` / `BLUETOOTH_SCAN` (and **CAMERA** if using QR).

`Geslamp-with-connection.aia` applies those fixes and keeps the QR UI.

## Wiring — Arduino Mega 2560

| Part | Mega pin |
|---|---|
| BLE/HC-05 VCC / GND | 5V / GND |
| Module **TXD** | **19 (RX1)** |
| Module **RXD** | **18 (TX1)** — voltage divider recommended |
| Servo signal | **9** |
| Servo red / brown | 5V / GND — external 5V better, shared GND |

**Two gotchas that cost time:**

- The Mega uses **Serial1**. Not SoftwareSerial — **pin 2 can't receive on the Mega**.
- On the Mega the Servo library (up to 12 servos) uses **Timer5** → **no PWM on pins 44, 45, 46**.
  Use pins 2–8 for LED PWM.

## Commands the app sends

All end with `#`. The fixed app also appends CR/LF after each command.

| Command | Meaning |
|---|---|
| `H<angle>#` | Head (45–135) |
| `E<angle>#` | Elbow (30–150) |
| `B<angle>#` | Base (0–350) |
| `B175#E90#H90#` | Reset position |
| `TW#` / `TN#` / `TC#` | Warm / Normal / Cool light |
| `P<0-100>#` | Brightness |
| `M1#` / `M0#` | Mobile / Gesture mode |
| `S<angle>#` | Servo test (test app only) |

Default rest pose in the app: base **175**, elbow **90**, head **90**.
**Gesture Mode** locks the phone servo buttons; **Mobile Mode** must be active to drive them.

## Tools / setup

- MIT App Inventor (ai2.appinventor.mit.edu) for the `.aia`.
- Serial Bluetooth Terminal — confirmed working against the module this session.
- VS Code + **PlatformIO IDE** extension (prior brain). Open the folder that **contains**
  `platformio.ini`. Serial Monitor **9600 baud**.

## Next steps

1. Confirm radio: **HC-05 or BLE** — don't mix the two `.aia` stacks.
2. Test `Geslamp-with-connection.aia` as an APK: CONNECT turns green, status shows `Sent: H95#`, servo moves.
3. Upload diagnostic Mega code if wiring is still in doubt (servo sweep / `S0#` / phone `BLE raw:` lines).
4. Full Arduino code for head / elbow / base + light if not already on the Mega.
5. Part 2: gesture mode.
