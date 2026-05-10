@echo off
cd /d "%~dp0"
title TOBO_VietSub Portable
if exist "TOBO_VietSub.exe" (
  start "" "%~dp0TOBO_VietSub.exe"
  exit /b
)
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" app.py
) else (
  call install_windows.bat
  if exist ".venv\Scripts\python.exe" ".venv\Scripts\python.exe" app.py
)
pause
