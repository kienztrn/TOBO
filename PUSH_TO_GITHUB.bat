@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Push TOBO_VietSub len GitHub TOBO

echo ==============================================
echo   PUSH TOBO VIETSUB LEN GITHUB: kienztrn/TOBO
echo ==============================================
echo.

git --version >nul 2>&1
if errorlevel 1 (
  echo [LOI] May chua co Git.
  echo Cai Git tai: https://git-scm.com/download/win
  echo Cai xong mo lai file nay.
  pause
  exit /b 1
)

if not exist ".git" (
  echo [1/5] Khoi tao Git repo local...
  git init
)

echo [2/5] Cau hinh nhanh branch main...
git branch -M main

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  echo [3/5] Them remote GitHub...
  git remote add origin https://github.com/kienztrn/TOBO.git
) else (
  echo [3/5] Cap nhat remote GitHub...
  git remote set-url origin https://github.com/kienztrn/TOBO.git
)

echo [4/5] Add va commit file...
git add .
git commit -m "Update TOBO VietSub auto updater v1.6.0" 2>nul
if errorlevel 1 (
  echo Khong co thay doi moi de commit, tiep tuc push.
)

echo [5/5] Push len GitHub...
echo Neu Git hoi dang nhap, hay dang nhap bang trinh duyet/token theo huong dan cua Git.
git push -u origin main
if errorlevel 1 (
  echo.
  echo [LOI] Push that bai.
  echo Nguyen nhan hay gap:
  echo - Chua dang nhap GitHub trong Git Credential Manager.
  echo - Repo khong rong va can pull truoc.
  echo - Tai khoan khong co quyen push vao kienztrn/TOBO.
  echo.
  echo Cach thu nhanh:
  echo   git pull origin main --allow-unrelated-histories
  echo   git push -u origin main
  pause
  exit /b 1
)

echo.
echo ==============================================
echo XONG! Da push len:
echo https://github.com/kienztrn/TOBO
echo ==============================================
echo.
pause
