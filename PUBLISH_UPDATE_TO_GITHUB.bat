@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Publish TOBO VietSub Update to GitHub

echo ==============================================
echo  PUBLISH UPDATE LEN GITHUB - kienztrn/TOBO
echo ==============================================
echo.
echo Script nay se day ban hien tai len GitHub.
echo App se doc update_manifest.json tren GitHub de tu cap nhat.
echo.

git --version >nul 2>&1
if errorlevel 1 (
  echo [LOI] May chua co Git. Cai Git for Windows truoc.
  pause
  exit /b 1
)

if not exist ".git" git init

git branch -M main

git remote get-url origin >nul 2>&1
if errorlevel 1 (
  git remote add origin https://github.com/kienztrn/TOBO.git
) else (
  git remote set-url origin https://github.com/kienztrn/TOBO.git
)

echo [1/4] Lay thay doi moi tren GitHub neu co...
git pull origin main --rebase --allow-unrelated-histories

echo [2/4] Add file...
git add -A

echo [3/4] Commit...
git commit -m "Publish TOBO VietSub update" 2>nul
if errorlevel 1 echo Khong co thay doi moi de commit, tiep tuc push.

echo [4/4] Push...
git push -u origin main
if errorlevel 1 (
  echo.
  echo [LOI] Push that bai. Kiem tra dang nhap GitHub/Credential Manager.
  pause
  exit /b 1
)

echo.
echo Da publish xong.
echo Manifest update:
echo https://raw.githubusercontent.com/kienztrn/TOBO/main/update_manifest.json
echo.
echo Tu cac ban sau, app co the bam Cap nhat de tu tai main.zip va tu ghi de file moi.
pause
