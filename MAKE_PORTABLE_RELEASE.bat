@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Make TOBO_VietSub Portable Release

echo ============================================
echo   TAO BAN PORTABLE GON CHO TOBO VIETSUB

echo ============================================

set OUT=release\TOBO_VietSub_Portable
if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%" >nul 2>&1
mkdir "%OUT%\assets" >nul 2>&1
mkdir "%OUT%\output" >nul 2>&1
mkdir "%OUT%\temp" >nul 2>&1
mkdir "%OUT%\updates" >nul 2>&1

if exist "dist\TOBO_VietSub.exe" (
  copy /y "dist\TOBO_VietSub.exe" "%OUT%\TOBO_VietSub.exe" >nul
) else (
  echo Chua co dist\TOBO_VietSub.exe, se tao portable source.
  copy /y app.py "%OUT%\app.py" >nul
  copy /y requirements.txt "%OUT%\requirements.txt" >nul
  copy /y install_windows.bat "%OUT%\install_windows.bat" >nul
  copy /y run_app.bat "%OUT%\run_app.bat" >nul
)

if exist "assets" xcopy /e /i /y "assets" "%OUT%\assets" >nul
if exist "update_config.json" copy /y update_config.json "%OUT%\update_config.json" >nul
if exist "update_manifest.json" copy /y update_manifest.json "%OUT%\update_manifest.json" >nul
if exist "tobo_update_helper.py" copy /y tobo_update_helper.py "%OUT%\tobo_update_helper.py" >nul
if exist "README.txt" copy /y README.txt "%OUT%\README.txt" >nul
copy /y RUN_PORTABLE.bat "%OUT%\RUN_PORTABLE.bat" >nul

> "%OUT%\HUONG_DAN_NHANH.txt" echo Chay RUN_PORTABLE.bat hoac TOBO_VietSub.exe neu co.
>> "%OUT%\HUONG_DAN_NHANH.txt" echo Thu muc output dung de chua file TXT.
>> "%OUT%\HUONG_DAN_NHANH.txt" echo Thu muc updates dung de chua ban cap nhat tai ve.
>> "%OUT%\HUONG_DAN_NHANH.txt" echo Muon auto update that su, dien manifest_url trong update_config.json.

echo.
echo Da tao portable tai:
echo %CD%\%OUT%
start "" "%CD%\%OUT%"
pause
