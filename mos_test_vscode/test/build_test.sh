#!/usr/bin/env bash
# Compile src/main.cpp against the desktop Arduino stub and run the harness.
# No board and no PlatformIO required -- just gcc.
set -u
cd "$(dirname "$0")/.."

OUT=$(mktemp -d)
FLAGS="-std=c++17 -Wall -Wextra -Wno-unused-parameter -O1"

echo "--- compiling sketch ---"
g++ $FLAGS -Itest/arduino_stub -c src/main.cpp -o "$OUT/main.o" || exit 1

echo "--- compiling harness ---"
g++ $FLAGS -Itest/arduino_stub -c test/harness.cpp -o "$OUT/harness.o" || exit 1

g++ "$OUT/main.o" "$OUT/harness.o" -o "$OUT/test" || exit 1

echo "--- running ---"
"$OUT/test"
STATUS=$?
rm -rf "$OUT"
exit $STATUS
