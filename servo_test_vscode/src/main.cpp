/*
  BASE SERVO + BLE test  -  Arduino Mega 2560

  Focused on the base joint (pin 9) so we can get ONE axis moving end to end
  before wiring up head / elbow / light.

  WHAT CHANGED vs the previous diagnostic
  ---------------------------------------
  1. servo.write() only accepts 0..180 and silently caps there. That is why the
     terminal log shows  S300#  ->  OK 180  and the base never used its full
     300 degrees. The servo is now driven with writeMicroseconds() over a
     calibratable pulse range, so 0..300 degrees is real travel.
     Do NOT "fix" this by writing  servo.write(2500)  : on AVR any value >= 544
     is reinterpreted as a pulse width in microseconds, so S600# would jump to
     ~600 us. Use writeMicroseconds(), as below.

  2. Commands that are not for the base (H.., E.., TW/TN/TC, M0/M1, P..) are
     logged and ignored instead of being parsed as an angle. Before, the app's
     TW# snapped the servo to 0, M1# to 1, P50# to 50.

  3. Every byte from the BLE module is printed with its number and a running
     total, so a baud mismatch shows up as garbage rather than silence.

  WIRING
  ------
    BLE TXD -> pin 19 (RX1)      BLE RXD -> pin 18 (TX1)
    BLE VCC -> 5V                BLE GND -> GND
    Servo signal -> pin 9        Servo red -> 5V      Servo brown -> GND
    (Mega + Servo library uses Timer5 -> do not use PWM on pins 44, 45, 46)

  COMMANDS ACCEPTED
  -----------------
    B<angle>#   base, 0..300      <- this is what the phone app sends
    S<angle>#   same, for typing by hand in the terminal

  Serial Monitor: 9600 baud
*/
#include <Arduino.h>
#include <Servo.h>

#define ble Serial1            // pins 19 (RX1) / 18 (TX1)
const int BASE_PIN = 9;

// Pulse width for 0 deg and for 300 deg. Narrow these if the servo buzzes or
// stalls at either end. Typical 300-degree servo: 500 .. 2500 us.
const int MIN_US  = 500;
const int MAX_US  = 2500;
const int MAX_DEG = 300;

Servo baseServo;
String bleBuf = "";
String usbBuf = "";
unsigned long bleBytes = 0;

void moveBase(int deg, const char *source) {
  deg = constrain(deg, 0, MAX_DEG);
  int us = map(deg, 0, MAX_DEG, MIN_US, MAX_US);
  baseServo.writeMicroseconds(us);
  Serial.print("["); Serial.print(source); Serial.print("] base -> ");
  Serial.print(deg); Serial.print(" deg ("); Serial.print(us); Serial.println(" us)");
  ble.print("OK "); ble.println(deg);
}

void handle(String cmd, const char *source) {
  cmd.trim();
  if (cmd.length() < 2) return;
  char kind = cmd[0];
  int val = cmd.substring(1).toInt();
  if (kind == 'B' || kind == 'S') {
    moveBase(val, source);
  } else {
    Serial.print("["); Serial.print(source); Serial.print("] not a base command, ignored: ");
    Serial.println(cmd);
  }
}

// collect characters until '#', then run the command
void feed(char c, String &buf, const char *source) {
  if (c == '#') { handle(buf, source); buf = ""; }
  else if (c != '\r' && c != '\n') { buf += c; if (buf.length() > 20) buf = ""; }
}

void setup() {
  Serial.begin(9600);
  ble.begin(9600);
  baseServo.attach(BASE_PIN, MIN_US, MAX_US);

  Serial.println();
  Serial.println("=== BASE SERVO + BLE ===");
  Serial.println("Sweep 0 -> 150 -> 0. Watch the base move.");
  moveBase(0,   "BOOT"); delay(1200);
  moveBase(150, "BOOT"); delay(1200);
  moveBase(0,   "BOOT"); delay(600);
  Serial.println("No movement? -> wiring or power, not Bluetooth.");
  Serial.println("Now press the base arrows in the phone app and watch here:");
  Serial.println("  clean characters -> data is arriving, the base should move");
  Serial.println("  255 / 254 garbage -> BAUD MISMATCH: try 38400, then 115200");
  Serial.println("  nothing at all -> not connected, or the module is in AT mode");
  Serial.println("Type B0#  or  B150#  here to test by hand.");
  Serial.println("Waiting...");
}

void loop() {
  // Bluetooth data
  while (ble.available()) {
    char c = ble.read();
    bleBytes++;
    Serial.print("BLE raw: '"); Serial.print(c); Serial.print("' (");
    Serial.print((int)(uint8_t)c); Serial.print(")  total=");
    Serial.println(bleBytes);
    feed(c, bleBuf, "BLE");
  }
  // Commands typed in the Serial Monitor
  while (Serial.available()) {
    feed((char)Serial.read(), usbBuf, "USB");
  }
}
