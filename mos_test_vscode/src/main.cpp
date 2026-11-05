/*
  XY-MOS MODULE + 5 V LED BOARD  --  PWM DIMMER TEST
  ==================================================

  This is the "does the wiring in the diagram work" sketch. Nothing else.
  It proves three things in order:
    1. the LED board lights at all  (wiring / power / ground)
    2. the module switches         (PWM high = ON, PWM low = OFF)
    3. PWM dims it smoothly        (brightness follows the duty cycle)


  WIRING THIS SKETCH EXPECTS
  --------------------------
    5 V supply +   ------------> VIN+      [XY-MOS]      OUT+ -----> LED board +
    5 V supply GND ------------> VIN-
    Mega pin 6     ------------> PWM
    Mega GND       ------------> GND

  *** The module GND pin and the 5 V supply GND must be the SAME node. ***
  If the supply feeds VIN+/VIN- and the ground only reaches the module through
  the supply's own negative, that is usually fine -- but if the LED flickers or
  never lights while the Mega looks happy, join Mega GND to supply GND with a
  wire and try again. That is the single most common cause.

  This is a LOW-SIDE switch, so the LED board's "-" is NOT grounded: OUT- is the
  switched side. Never connect OUT- to ground while it is switching -- that
  shorts the 5 V supply through the MOSFET. Measure nothing across OUT+/OUT-
  with a meter expecting 5 V; the low side is switching, so the voltages at
  both OUT pins move together.


  COMMANDS -- Serial Monitor, 115200 baud, "Newline" ending
  ---------------------------------------------------------
    T          timed test  100% -> off -> 25% -> 50% -> 75% -> 100% -> off
    S          smooth fade  0 -> 100% -> 0   (4 s, look for stepping/flicker)
    L          leave it fully ON  (measure current here)
    R          OFF / reset to 0
    0..255     set a level directly, e.g.  128
    X          STOP -- aborts any test in progress
    ?          print this list again

  Pin 6 on a Mega runs at ~490 Hz by default, which is fine for an LED and
  avoids audible buzz from the MOSFET's mechanical neighbours. On ESP32 the
  sketch uses 1 kHz / 8-bit hardware PWM.


  WHAT "IT WORKS" LOOKS LIKE
  --------------------------
    boot flashes      -> LED blinks 3 times, then goes dark
    L                -> full brightness, steady, no flicker
    128              -> about half brightness, steady
    S                -> even fade both ways, no stepping or dropouts
    an "X" mid-test  -> LED snaps off immediately


  IF IT DOESN'T WORK
  ------------------
    never lights at all      -> check VIN+/VIN- polarity, then join the grounds
    lights but ignores PWM   -> PWM wire not on pin 6, or swapped with GND
    dims only a little       -> module's PWM input wants a logic HIGH; a 5 V
                                Mega is correct, a 3.3 V board may not be
    LED board very dim       -> supply can't hold 5 V; check its current rating
    flicker while fading     -> normal for cheap modules at very low duty

  Power: "5 V, 5730" boards are often 5-15 W. Check the supply's rating before
  leaving it at 100% (command L) for a long time.
*/

#include <Arduino.h>

// ==================== EDIT IF YOUR WIRING DIFFERS ====================
const uint8_t  PWM_PIN  = 6;     // Mega pin 6 -- the diagram. ESP32: 18 is safe.
const uint16_t PWM_HZ   = 1000;  // only affects ESP32; AVR pin 6 is fixed ~490 Hz
const uint8_t  PWM_BITS = 8;     // 8-bit -> levels 0..255
// =====================================================================

const int  MAX_LEVEL   = (1 << PWM_BITS) - 1;
const long SERIAL_BAUD = 115200;

int      level          = 0;
bool     abortRequested = false;
String   cmdBuf         = "";

void pollSerial();   // defined lower down; the blocking waits call it

// ------------------------------------------------------------------ PWM
void pwmBegin() {
#if defined(ARDUINO_ARCH_ESP32)
  #if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcAttach(PWM_PIN, PWM_HZ, PWM_BITS);
  #else
    ledcSetup(0, PWM_HZ, PWM_BITS);
    ledcAttachPin(PWM_PIN, 0);
  #endif
#else
  pinMode(PWM_PIN, OUTPUT);
  analogWrite(PWM_PIN, 0);
#endif
}

void pwmWrite(int v) {
#if defined(ARDUINO_ARCH_ESP32)
  #if ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcWrite(PWM_PIN, v);
  #else
    ledcWrite(0, v);
  #endif
#else
  analogWrite(PWM_PIN, v);
#endif
}

// Set a level and report it. report=false is used inside fades so the serial
// monitor doesn't scroll 255 lines in four seconds.
void setLevel(int v, bool report = true) {
  level = constrain(v, 0, MAX_LEVEL);
  pwmWrite(level);
  if (report) {
    Serial.print(F("[pwm] level="));
    Serial.print(level);
    Serial.print(F("  duty="));
    Serial.print((int)(level * 100L / MAX_LEVEL));
    Serial.println('%');
  }
}

// ------------------------------------------------------------- serial in
void printHelp() {
  Serial.println(F("---------------------------------------------"));
  Serial.println(F("T  timed test      S  smooth fade      L  full ON"));
  Serial.println(F("R  off             0..255 set level    X  STOP"));
  Serial.println(F("?  this list"));
  Serial.println(F("---------------------------------------------"));
}

// ------------------------------------------------------------------ tests
// Waits, but keeps reading serial so X can abort mid-test.
bool waitFor(uint16_t ms) {
  unsigned long start = millis();
  while (millis() - start < ms) {
    // let the command handler see anything typed while we wait
    abortRequested = false;
    pollSerial();
    if (abortRequested) return false;
    delay(10);
  }
  return true;
}

bool fadeTo(int target, uint16_t ms) {
  int from = level;
  unsigned long start = millis();
  while (millis() - start < ms) {
    unsigned long el = millis() - start;
    level = from + (int)((long)(target - from) * (long)el / (long)ms);
    level = constrain(level, 0, MAX_LEVEL);
    pwmWrite(level);
    abortRequested = false;
    pollSerial();
    if (abortRequested) return false;
    delay(10);
  }
  setLevel(target);
  return true;
}

void timedTest() {
  Serial.println(F("[test] timed sequence -- X to stop"));
  const int steps[] = {MAX_LEVEL, 0, MAX_LEVEL / 4, MAX_LEVEL / 2, (MAX_LEVEL * 3) / 4, MAX_LEVEL, 0};
  const uint16_t hold[] = {2000, 1000, 1500, 1500, 1500, 2000, 0};
  for (uint8_t i = 0; i < sizeof(steps) / sizeof(steps[0]); i++) {
    setLevel(steps[i]);
    if (hold[i] && !waitFor(hold[i])) { setLevel(0); Serial.println(F("[test] aborted")); return; }
  }
  Serial.println(F("[test] done -- back to 0"));
}

void sweepTest() {
  Serial.println(F("[test] fade 0 -> 100% -> 0 -- X to stop"));
  if (!fadeTo(MAX_LEVEL, 2000)) { setLevel(0); Serial.println(F("[test] aborted")); return; }
  if (!fadeTo(0, 2000))         { setLevel(0); Serial.println(F("[test] aborted")); return; }
  Serial.println(F("[test] done -- back to 0"));
}

// ------------------------------------------------------- command handler
void handleCommand(String cmd) {
  cmd.trim();
  if (!cmd.length()) return;
  cmd.toUpperCase();
  char c0 = cmd[0];

  if (cmd == "?")                    { printHelp(); }
  else if (cmd == "T")               { timedTest(); }
  else if (cmd == "S")               { sweepTest(); }
  else if (cmd == "L")               { setLevel(MAX_LEVEL); }
  else if (cmd == "R")               { setLevel(0); }
  else if (cmd == "X" || cmd == "STOP") { abortRequested = true; setLevel(0); Serial.println(F("[stop]")); }
  else if ((c0 >= '0' && c0 <= '9') || c0 == '-') { setLevel(cmd.toInt()); }
  else {
    Serial.print(F("[pwm] unknown command: "));
    Serial.println(cmd);
    printHelp();
  }
}

void pollSerial() {
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') { handleCommand(cmdBuf); cmdBuf = ""; }
    else if (cmdBuf.length() < 24) { cmdBuf += c; }
    else { cmdBuf = ""; }               // runaway input, drop it
  }
}

// ------------------------------------------------------------- lifecycle
void setup() {
  Serial.begin(SERIAL_BAUD);
  pwmBegin();
  delay(300);                            // let USB serial attach

  Serial.println();
  Serial.println(F("=== XY-MOS PWM DIMMER TEST ==="));
  Serial.print(F("PWM pin "));
  Serial.print(PWM_PIN);
  Serial.println(F("  (PWM HIGH = ON, this is a low-side switch)"));

  // Wiring self-test: three short flashes. If these don't appear, stop here --
  // the problem is power/ground, not software.
  Serial.println(F("[boot] 3 flashes at 40% ..."));
  for (uint8_t i = 0; i < 3; i++) {
    pwmWrite(MAX_LEVEL * 40 / 100); delay(250);
    pwmWrite(0);                    delay(250);
  }
  level = 0;
  Serial.println(F("[boot] no flash? -> polarity of VIN+/VIN-, or grounds not joined"));

  printHelp();
  Serial.println(F("[ready] type a command"));
}

void loop() {
  pollSerial();
}
