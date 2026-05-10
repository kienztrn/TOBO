@echo off
setlocal
cd /d "%~dp0"
title Build TOBO_VietSub.exe

echo ==========================================
echo  Build file EXE cho TOBO VietSub
echo ==========================================

if not exist ".venv\Scripts\python.exe" (
  call install_windows.bat
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pyinstaller

set ADD_FFMPEG=
if exist "ffmpeg\bin\ffmpeg.exe" set ADD_FFMPEG=--add-data "ffmpeg;ffmpeg"

set ADD_ASSETS=
if exist "assets" set ADD_ASSETS=--add-data "assets;assets"

set ADD_HELPER=
if exist "tobo_update_helper.py" set ADD_HELPER=--add-data "tobo_update_helper.py;."

set APP_ICON=
if exist "assets\app_icon.ico" set APP_ICON=--icon "assets\app_icon.ico"

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name TOBO_VietSub ^
  --collect-all faster_whisper ^
  --collect-all ctranslate2 ^
  --collect-all av ^
  --collect-all tokenizers ^
  --collect-all huggingface_hub ^
  --collect-all deep_translator ^
  %ADD_FFMPEG% ^
  %ADD_ASSETS% ^
  %ADD_HELPER% ^
  %APP_ICON% ^
  app.py

echo.
echo Neu build thanh cong, file nam tai: dist\TOBO_VietSub.exe
echo Logo meo, helper auto-update va UI future da duoc nhung vao ban build.
echo Luu y: Lan dau chay model Whisper van co the can Internet de tai model.
pause
