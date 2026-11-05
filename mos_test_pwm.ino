/*
  PWM DIMMER  --  XY-MOS module, low-side switch, single LED board
  ================================================================

  Use this if you just want the LED fading, not a serial test bench.
  (mos_test_vscode/ is the full test version with commands and a self-check.)

  WIRING
  ------
    5 V supply +  -> VIN+          LED board +  -> OUT+
    5 V supply -  -> VIN-          LED board -  -> OUT-
    Mega pin 6    -> PWM
    Mega GND      -> GND        <- must share ground with the 5 V supply
    (or ESP32 pin 18)

  This is a LOW-SIDE switch: PWM high = ON, PWM low = OFF. Never connect OUT- to
  ground -- it is the switched node and grounding it shorts the 5 V supply.

  Pin 6 on a Mega is ~490 Hz, plenty for an LED. Don't move it to pins 44-46;
  the Servo library owns that timer when the robot arm firmware is flashed.

  After uploading, open the Serial Monitor at 115200 to see what it's doing.
*/

#include <Arduino.h>

const uint8_t PWM_PIN   = 6;
const uint16_t PWM_HZ   = 1000;   // ESP32 only; AVR pin 6 is fixed ~490 Hz
const uint8_t PWM_BITS  = 8;      // 0..255
const int     MAX_LEVEL = (1 << PWM_BITS) - 1;

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
  analogWrite(PWM_PIN, constrain(v, 0, MAX_LEVEL));
#endif
}

void setup() {
  Serial.begin(115200);
  pwmBegin();
  Serial.println(F("XY-MOS PWM dimmer: low-side switch, PWM high = ON"));
}

void loop() {
  // Fade up, fade down, forever.
  for (int v = 0; v <= MAX_LEVEL; v += 5) { pwmWrite(v); delay(30); }
  for (int v = MAX_LEVEL; v >= 0; v -= 5) { pwmWrite(v); delay(30); }
  delay(800);
}
