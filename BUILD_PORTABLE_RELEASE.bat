@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title TOBO_VietSub - Build Portable Release
color F5

echo ==============================================
echo      TOBO VIETSUB - BUILD PORTABLE RELEASE

echo ==============================================
echo.

echo [1/7] Kiem tra Python...
py -3 --version >nul 2>&1
if errorlevel 1 (
  python --version >nul 2>&1
  if errorlevel 1 (
    echo [LOI] Khong tim thay Python 3. Cai Python 3.10+ truoc, nho tick Add Python to PATH.
    pause
    exit /b 1
  )
  set PYTHON_CMD=python
) else (
  set PYTHON_CMD=py -3
)

echo [2/7] Tao .venv neu can...
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

echo [3/7] Cai thu vien build...
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo [LOI] Cai thu vien that bai. Chup man hinh loi gui lai.
  pause
  exit /b 1
)

echo [4/7] Don build cu...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist release rmdir /s /q release

echo [5/7] Build portable dang thu muc onedir...
set ADD_FFMPEG=
if exist "ffmpeg\bin\ffmpeg.exe" set ADD_FFMPEG=--add-data "ffmpeg;ffmpeg"
set ADD_ASSETS=
if exist "assets" set ADD_ASSETS=--add-data "assets;assets"
set APP_ICON=
if exist "assets\app_icon.ico" set APP_ICON=--icon "assets\app_icon.ico"

pyinstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
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
  %APP_ICON% ^
  app.py

if errorlevel 1 (
  echo [LOI] Build portable that bai.
  pause
  exit /b 1
)

echo [6/7] Tao cau truc release gon...
mkdir release >nul 2>&1
xcopy dist\TOBO_VietSub release\TOBO_VietSub_Portable\ /E /I /Y /Q >nul
mkdir release\TOBO_VietSub_Portable\output >nul 2>&1
mkdir release\TOBO_VietSub_Portable\temp >nul 2>&1
copy /y README.txt release\TOBO_VietSub_Portable\README.txt >nul
copy /y update_config.json release\TOBO_VietSub_Portable\update_config.json >nul
copy /y update_manifest.example.json release\TOBO_VietSub_Portable\update_manifest.example.json >nul

> release\TOBO_VietSub_Portable\CHAY_APP.txt echo Mo file TOBO_VietSub.exe de chay app.
>> release\TOBO_VietSub_Portable\CHAY_APP.txt echo Neu muon updater hoat dong, sua update_config.json va dien URL manifest.

echo [7/7] Nen ZIP portable neu PowerShell ho tro...
if exist release\TOBO_VietSub_Portable.zip del /q release\TOBO_VietSub_Portable.zip
powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path 'release\TOBO_VietSub_Portable' -DestinationPath 'release\TOBO_VietSub_Portable.zip' -Force" >nul 2>&1

echo.
echo ==============================================
echo BUILD PORTABLE XONG ROI!
echo Thu muc portable:
echo   %CD%\release\TOBO_VietSub_Portable
if exist release\TOBO_VietSub_Portable.zip echo File ZIP: %CD%\release\TOBO_VietSub_Portable.zip
echo ==============================================
start "" "%CD%\release"
pause
