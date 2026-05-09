@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title TOBO_VietSub - Build EXE 1 Click
color F5

echo ==============================================
echo      TOBO VIETSUB - BUILD EXE 1 CLICK

echo ==============================================
echo.

echo [1/6] Kiem tra Python...
py -3 --version >nul 2>&1
if errorlevel 1 (
  python --version >nul 2>&1
  if errorlevel 1 (
    echo [LOI] Khong tim thay Python 3.
    echo Hay cai Python 3.10+ truoc: https://www.python.org/downloads/windows/
    echo NHO tick vao o Add Python to PATH khi cai.
    pause
    exit /b 1
  )
  set PYTHON_CMD=python
) else (
  set PYTHON_CMD=py -3
)

echo [2/6] Tao moi truong .venv neu can...
if not exist ".venv\Scripts\python.exe" (
  %PYTHON_CMD% -m venv .venv
  if errorlevel 1 (
    echo [LOI] Khong tao duoc .venv
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [LOI] Khong kich hoat duoc .venv
  pause
  exit /b 1
)

echo [3/6] Cai thu vien can thiet...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :pip_fail
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 goto :pip_fail

echo [4/6] Don dep ban build cu...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist release rmdir /s /q release

echo [5/6] Build file EXE...
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

if errorlevel 1 (
  echo.
  echo [LOI] Build EXE that bai.
  echo Neu loi lien quan den Visual C++ runtime, hay cai Microsoft VC++ Redistributable.
  pause
  exit /b 1
)

echo [6/6] Tao goi release san dung...
mkdir release\TOBO_VietSub >nul 2>&1
copy /y dist\TOBO_VietSub.exe release\TOBO_VietSub\TOBO_VietSub.exe >nul
mkdir release\TOBO_VietSub\output >nul 2>&1
mkdir release\TOBO_VietSub\temp >nul 2>&1
copy /y README.txt release\TOBO_VietSub\README.txt >nul
if exist update_config.json copy /y update_config.json release\TOBO_VietSub\update_config.json >nul
mkdir release\TOBO_VietSub\updates >nul 2^>^&1

> release\TOBO_VietSub\RUN_ME.txt echo Mo file TOBO_VietSub.exe de dung app.
>> release\TOBO_VietSub\RUN_ME.txt echo.
>> release\TOBO_VietSub\RUN_ME.txt echo Neu gap file media la va can fallback, hay cai FFmpeg bang lenh:
>> release\TOBO_VietSub\RUN_ME.txt echo winget install Gyan.FFmpeg

echo.
echo ==============================================
echo BUILD XONG ROI!
echo File EXE nam o:
echo   %CD%\release\TOBO_VietSub\TOBO_VietSub.exe
echo ==============================================
echo.
start "" "%CD%\release\TOBO_VietSub"
pause
exit /b 0

:pip_fail
echo.
echo [LOI] Cai thu vien that bai.
echo Thu dong PowerShell/CMD va chay lai file nay voi quyen thuong.
echo Neu van loi, hay chup man hinh loi roi gui toi.
pause
exit /b 1
