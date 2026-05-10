@echo off
setlocal
cd /d "%~dp0"
title Install TOBO VietSub

echo ==========================================
echo  Cai thu vien cho TOBO VietSub
echo ==========================================

py -3 --version >nul 2>&1
if errorlevel 1 (
  python --version >nul 2>&1
  if errorlevel 1 (
    echo Khong tim thay Python. Hay cai Python 3.10+ truoc.
    echo Link: https://www.python.org/downloads/windows/
    pause
    exit /b 1
  )
  set PYTHON_CMD=python
) else (
  set PYTHON_CMD=py -3
)

if not exist ".venv\Scripts\python.exe" (
  echo Tao moi moi truong .venv...
  %PYTHON_CMD% -m venv .venv
)

call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Da cai xong thu vien Python.
echo.
echo GHI CHU:
echo - Ban moi uu tien doc video truc tiep, nhieu file KHONG can FFmpeg nua.
echo - Neu gap file la/loi codec, cai FFmpeg de fallback:
echo   winget install Gyan.FFmpeg

echo.
echo Chay app bang file run_app.bat
pause
