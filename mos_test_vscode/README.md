# XY-MOS PWM dimmer test — Arduino Mega 2560

A single sketch that tests the wiring you drew: **5 V supply → XY-MOS module → 5 V LED board**,
with the module's `PWM` input from **pin 6** and a common ground.

```
5 V supply +  ──────────────► VIN+      ┌──────────┐      OUT+ ──────────► LED board +
5 V supply −  ──────────────► VIN−      │  XY-MOS  │      OUT− ──────────► LED board −
                                        │(low-side)│
Mega pin 6   ──────────────► PWM        │          │
Mega GND     ──────────────► GND        └──────────┘
```

## 1. Flash it

Open **this folder** (`mos_test_vscode/`, the one containing `platformio.ini`) in VS Code with the
PlatformIO extension, then **Build** and **Upload**. It defaults to `megaatmega2560`; uncomment the
ESP32 block in `platformio.ini` if you're on one.

Serial Monitor: **115200 baud**, line ending **Newline**.

## 2. Run it

At boot the LED flashes **3 times at 40%** and goes dark. That flash is the wiring test — if it
doesn't happen, nothing after it matters (see §5).

| Type this | What happens |
|---|---|
| `L` | Full ON. Leave it here to check the supply isn't sagging. |
| `128` | Half brightness. Steady = PWM is working. |
| `0` | Off. |
| `S` | Smooth fade 0 → 100% → 0 over 4 s. Look for even fading, no flicker. |
| `T` | Timed sequence: 100% → off → 25% → 50% → 75% → 100% → off. |
| `X` | Abort whatever is running and turn the output off. |
| `?` | Print the command list. |
| `0`–`255` | Any level directly. |

## 3. What "it works" looks like

- boot flash appears → power and ground are fine
- `L` gives steady full brightness → module is switching
- `128` is visibly dimmer than `L` and holds steady → PWM is reaching the module
- `S` fades evenly both directions → no software problem left

Any of those failing points at wiring, not code.

## 4. Don't-do list for this circuit

- **Don't tie `OUT−` to ground.** This is a low-side switch; `OUT−` *is* the switched node.
  Grounding it shorts the 5 V rail through the MOSFET.
- **Don't expect 5 V across `OUT+`/`OUT−`.** Measure from `OUT+` to the supply ground
  (≈5 V whenever the LED is on), not across the output pair.
- **Don't run a 3.3 V board without checking.** The module wants a real logic HIGH on `PWM`.
  A 5 V Mega is right; a 3.3 V board may only switch weakly.

## 5. If nothing lights

| Symptom | First thing to check |
|---|---|
| Never lights, serial looks fine | `VIN+` / `VIN−` polarity, then **join Mega GND to supply GND with a wire** |
| Lights, ignores PWM | `PWM` wire is on pin 6, not swapped with `GND` |
| Dims only slightly | `PWM` input not reaching a full logic HIGH, or stuck at 3.3 V |
| Flickers under load | supply too small — a "5 V, 5730" board is often 5–15 W |
| Boot flash OK, everything else dead | sketch uploaded but serial is at the wrong baud — set 115200 |

## 6. Test the logic without hardware

`test/` compiles the real `src/main.cpp` against a stub `Arduino.h` and drives it with fake serial
input and fake time, so command parsing, levels, fades and abort can be verified on a laptop:

```bash
bash test/build_test.sh
```

It needs only `g++`. It cannot verify the MOSFET or the wiring — that's the board's job.

## 7. Power note

Check the supply's rating before holding 100% for long. If the LED board pulls more than the supply
can give, the 5 V rail sags and the module's behaviour gets confusing — bring the level down with
`128` and see whether the flicker stops before blaming the module.
