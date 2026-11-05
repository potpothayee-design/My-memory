// Desktop test harness for src/main.cpp.
// Compiles the real sketch against a stub Arduino and drives it with fake
// serial input and fake time, then asserts on the PWM pin value.
//
//   bash test/build_test.sh
//
// This checks the LOGIC only (command parsing, levels, fade, abort). It cannot
// tell you whether the MOSFET is wired correctly -- that needs the board.
#include <Arduino.h>

#include <cstdio>
#include <iostream>

unsigned long g_millis = 0;
int g_pwm_pin_value = -1;
std::string g_serial_in;
std::string g_serial_out;
std::vector<std::pair<unsigned long, int>> g_pwm_log;
SerialShim Serial;

void setup();
void loop();

static int failures = 0;

static void check(bool ok, const std::string &what) {
  std::printf("%s  %s\n", ok ? "PASS" : "FAIL", what.c_str());
  if (!ok) failures++;
}

// Feed a line, then let loop() consume it.
static void send(const std::string &line) {
  g_serial_in += line + "\n";
  loop();
}

int main() {
  std::printf("== boot ==\n");
  setup();
  check(g_pwm_pin_value == 0, "after boot the LED is off (level 0)");

  int flashes = 0;
  for (size_t i = 1; i < g_pwm_log.size(); i++)
    if (g_pwm_log[i - 1].second == 0 && g_pwm_log[i].second > 0) flashes++;
  check(flashes == 3, "boot does 3 self-test flashes (got " + std::to_string(flashes) + ")");

  std::printf("\n== manual levels ==\n");
  send("L");
  check(g_pwm_pin_value == 255, "L -> full on (255)");

  send("128");
  check(g_pwm_pin_value == 128, "128 -> level 128");

  send("0");
  check(g_pwm_pin_value == 0, "0 -> off");

  send("999");
  check(g_pwm_pin_value == 255, "999 clamps to 255");

  send("-5");
  check(g_pwm_pin_value == 0, "-5 clamps to 0");

  send("r");
  check(g_pwm_pin_value == 0, "lowercase r works (off)");

  std::printf("\n== fade (S) ==\n");
  size_t before = g_pwm_log.size();
  unsigned long t0 = g_millis;
  send("S");
  check(g_pwm_pin_value == 0, "fade ends back at 0");
  check(g_millis - t0 >= 4000, "fade takes about 4 s of virtual time");

  bool rose = false, fell = false, monotonic = true;
  int peak = -1, prev = -1;
  for (size_t i = before; i < g_pwm_log.size(); i++) {
    int v = g_pwm_log[i].second;
    if (prev >= 0) {
      if (v >= prev && !fell) rose = true;
      if (v <= prev && v < prev) fell = true;
      if (v > prev && fell) monotonic = false;  // must not rise after falling
    }
    if (v > peak) peak = v;
    prev = v;
  }
  check(peak == 255, "fade reaches full brightness");
  check(rose && fell, "fade goes up then down");
  check(monotonic, "fade never jumps back up after coming down");
  check(g_pwm_log.size() - before > 50, "fade actually steps, not a single jump");

  std::printf("\n== timed test (T) ==\n");
  t0 = g_millis;
  send("T");
  check(g_pwm_pin_value == 0, "timed test ends at 0");
  check(g_millis - t0 >= 9000, "timed test holds each step");

  std::printf("\n== abort (X) ==\n");
  // Queue T and X together: T starts inside loop(), and X must be seen by the
  // poll inside the blocking wait.
  g_serial_in += "T\nX\n";
  loop();
  check(g_pwm_pin_value == 0, "X aborts the timed test and leaves it off");
  check(g_serial_out.find("[test] aborted") != std::string::npos ||
        g_serial_out.find("[test] done") != std::string::npos,
        "abort path reports itself");

  std::printf("\n== bad input ==\n");
  send("hello");
  check(g_serial_out.find("unknown command") != std::string::npos,
        "garbage input is reported, not parsed as a level");
  check(g_pwm_pin_value == 0, "garbage input leaves the output alone");

  send("?");
  check(g_serial_out.find("T  timed test") != std::string::npos, "? prints the help");

  std::printf("\n== serial output ==\n");
  check(g_serial_out.find("XY-MOS PWM DIMMER TEST") != std::string::npos, "banner printed");
  check(g_serial_out.find("unknown command") != std::string::npos, "unknown-command message printed");
  check(g_serial_out.size() < 20000, "serial output stays small (" +
                                         std::to_string(g_serial_out.size()) + " chars)");

  std::printf("\n%d failure(s)\n", failures);
  return failures ? 1 : 0;
}
