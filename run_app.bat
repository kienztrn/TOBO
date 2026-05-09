@echo off
cd /d "%~dp0"
title TOBO VietSub

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" app.py
) else (
  echo Chua cai thu vien. Dang chay install_windows.bat truoc...
  call install_windows.bat
  if exist ".venv\Scripts\python.exe" ".venv\Scripts\python.exe" app.py
)
pause
