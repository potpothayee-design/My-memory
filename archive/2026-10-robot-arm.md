# Robot arm — BLE + Arduino Mega (2026-10)

**Cold layer.** Fetched only when the topic is the robot arm, BLE, Arduino, servos, the `.aia`
apps, or PlatformIO. Not loaded by default.

---

## What it is

A robot arm — head, elbow, base, plus a light — driven by an **Arduino Mega 2560** and controlled
from an **Android app over BLE**.

## Files

| File | What it is |
|---|---|
| `final_sure_part_1.aia` | Original app. **Classic Bluetooth — does NOT work with my module** |
| `final_sure_part_1_ble.aia` | Main app, converted to BLE, direct-connect to the module |
| `BLE_Test.aia` | Small test app: connect, log, servo 0/90/180 buttons, slider |
| `servo_test_vscode/` | PlatformIO project for the Mega (diagnostic servo + BLE) |

## Wiring — Arduino Mega 2560

| Part | Mega pin |
|---|---|
| BLE VCC / GND | 5V / GND |
| BLE **TXD** | **19 (RX1)** |
| BLE **RXD** | **18 (TX1)** — voltage divider recommended |
| Servo signal | **9** |
| Servo red / brown | 5V / GND — external 5V better, shared GND |

**Two gotchas that cost time:**

- The Mega uses **Serial1**. Not SoftwareSerial — **pin 2 can't receive on the Mega**.
- On the Mega the Servo library (up to 12 servos) uses **Timer5** → **no PWM on pins 44, 45, 46**.
  Use pins 2–8 for LED PWM.

## Commands the app sends

All end with `#`.

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

## App fixes already made

- Bluetooth permission requests added (Android 12+: `BLUETOOTH_CONNECT` / `BLUETOOTH_SCAN`;
  location for older versions).
- Hold-to-repeat buttons fixed — `HoldClock` / `RepeatClock` were never enabled, `TouchUp` was empty.
- `RepeatClock` used `<` instead of `=` — fixed.
- Brightness slider no longer floods Bluetooth (only sends on change).
- Removed unused QR scanner and duplicate connect button.

## Tools / setup

- VS Code + **PlatformIO IDE** extension. The C/C++ extension pack isn't needed.
- Open the folder that **contains** `platformio.ini` directly, or includes show red errors.
- Bottom bar: Build, Upload, Serial Monitor (**9600 baud**).
- **Only one device can connect to the BLE module at a time** — close Serial Bluetooth Terminal
  first.

## Next steps

1. Upload the diagnostic code and check the 3 tests:
   - **Test 1:** does the servo sweep at reset? No → wiring/power.
   - **Test 2:** type `S0#` in Serial Monitor — does the servo move?
   - **Test 3:** do the phone buttons show `BLE raw:` lines? No → swap pins 18/19, or try 115200 baud.
2. Write the full Arduino code for head / elbow / base + light.
3. Test `final_sure_part_1_ble.aia` against the full code.
4. Part 2: gesture mode.
5. _(The source list ended mid-item — step 5 was never written down. Ask, don't guess.)_
