@echo off
rem  hand_tracking one-click launcher (Windows)
rem  Double-click: webcam + window.  Any arguments are passed straight through:
rem     run_windows.bat --source 1 --max-hands 1
rem     run_windows.bat --serial COM5 --baud 9600
setlocal
cd /d "%~dp0"

set "PY=python"
where py >nul 2>nul
if not errorlevel 1 set "PY=py -3"

if not exist ".venv\Scripts\python.exe" (
  echo Creating the virtual environment ^(one time, about 30 seconds^)...
  %PY% -m venv .venv
  if errorlevel 1 goto :nopython
)

set "VPY=.venv\Scripts\python.exe"
"%VPY%" -c "import mediapipe, cv2, numpy" >nul 2>nul
if errorlevel 1 (
  echo Installing mediapipe, OpenCV, NumPy ^(one time, about 90 MB^)...
  "%VPY%" -m pip install --upgrade pip >nul
  "%VPY%" -m pip install -r requirements.txt
  if errorlevel 1 goto :pipfail
)

"%VPY%" hand_landmarker.py %*
if errorlevel 1 (
  echo.
  echo The program exited with an error - the message is above.
  pause
)
exit /b 0

:nopython
echo.
echo Python 3.9-3.12 was not found.
echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
pause
exit /b 1

:pipfail
echo.
echo Package install failed. Check the network, or run: .venv\Scripts\pip install -r requirements.txt
pause
exit /b 1
