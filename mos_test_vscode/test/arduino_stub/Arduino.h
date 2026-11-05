// Minimal host-side Arduino stub so the sketch's logic can be compiled and
// exercised with gcc on a laptop -- no board, no PlatformIO needed.
// Used only by test/build_test.sh. Not part of the firmware.
#pragma once

#include <cstdint>
#include <cstdlib>
#include <cctype>
#include <string>
#include <vector>
#include <utility>

typedef uint8_t byte;

extern unsigned long g_millis;
extern int g_pwm_pin_value;
extern std::string g_serial_in;
extern std::string g_serial_out;
extern std::vector<std::pair<unsigned long, int>> g_pwm_log;

inline unsigned long millis() { return g_millis; }
inline void delay(unsigned long ms) { g_millis += ms; }

#define F(x) (x)

template <typename T> T constrain(T v, T lo, T hi) { return v < lo ? lo : (v > hi ? hi : v); }

class SerialShim {
public:
  void begin(unsigned long) {}
  int available() { return (int)g_serial_in.size(); }
  int read() {
    if (g_serial_in.empty()) return -1;
    char c = g_serial_in[0];
    g_serial_in.erase(0, 1);
    return (unsigned char)c;
  }
  void print(const char *s) { g_serial_out += s; }
  void print(const std::string &s) { g_serial_out += s; }
  void print(char c) { g_serial_out += c; }
  void print(unsigned char v) { g_serial_out += std::to_string((int)v); }
  void print(int v) { g_serial_out += std::to_string(v); }
  void print(unsigned int v) { g_serial_out += std::to_string(v); }
  void print(long v) { g_serial_out += std::to_string(v); }
  void print(unsigned long v) { g_serial_out += std::to_string(v); }
  void println() { g_serial_out += "\n"; }
  template <typename T> void println(T v) { print(v); g_serial_out += "\n"; }
};
extern SerialShim Serial;

// Just enough of Arduino's String for the sketch: length / trim / toInt /
// toUpperCase / += / ==.
class String : public std::string {
public:
  String() {}
  String(const char *s) : std::string(s) {}
  String(const std::string &s) : std::string(s) {}
  unsigned int length() const { return (unsigned int)std::string::size(); }
  void trim() {
    size_t b = find_first_not_of(" \t\r\n");
    size_t e = find_last_not_of(" \t\r\n");
    if (b == std::string::npos) { clear(); return; }
    *this = substr(b, e - b + 1);
  }
  void toUpperCase() {
    for (auto &ch : *this) ch = (char)toupper((unsigned char)ch);
  }
  long toInt() const { return atol(c_str()); }
  String &operator+=(char c) { push_back(c); return *this; }
  String &operator+=(const char *s) { append(s); return *this; }
};

#define OUTPUT 1
#define INPUT 0
inline void pinMode(int, int) {}
inline void analogWrite(int, int v) {
  g_pwm_pin_value = v;
  if (g_pwm_log.empty() || g_pwm_log.back().second != v)
    g_pwm_log.push_back({g_millis, v});
}
