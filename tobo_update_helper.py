import os
import sys
import time
import zipfile
import shutil
import subprocess
from pathlib import Path

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    "output", "temp", "updates", "build", "dist", "release",
    ".mypy_cache", ".pytest_cache"
}

EXCLUDE_FILES = {
    "background_cloudfront.mp4",
}

def log(msg: str):
    print(msg, flush=True)

def find_source_root(extract_dir: Path) -> Path:
    candidates = []
    for path in extract_dir.rglob("app.py"):
        parent = path.parent
        # Ưu tiên thư mục app thật có requirements hoặc run_app
        score = 0
        if (parent / "requirements.txt").exists():
            score += 3
        if (parent / "run_app.bat").exists():
            score += 2
        if (parent / "assets").exists():
            score += 1
        candidates.append((score, parent))
    if not candidates:
        raise RuntimeError("Không tìm thấy app.py trong gói cập nhật.")
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]

def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDE_DIRS:
        return True
    if path.name in EXCLUDE_FILES:
        return True
    return False

def copy_update_files(src_root: Path, app_dir: Path):
    copied = 0
    for src in src_root.rglob("*"):
        rel = src.relative_to(src_root)
        if should_skip(rel):
            continue
        dst = app_dir / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    return copied

def restart_app(app_dir: Path):
    run_bat = app_dir / "run_app.bat"
    exe_candidates = [
        app_dir / "TOBO_VietSub.exe",
        app_dir / "VietSubTXT.exe",
    ]
    try:
        if run_bat.exists():
            subprocess.Popen(["cmd", "/c", "start", "", str(run_bat)], cwd=str(app_dir), shell=False)
            return
        for exe in exe_candidates:
            if exe.exists():
                subprocess.Popen([str(exe)], cwd=str(app_dir))
                return
        app_py = app_dir / "app.py"
        if app_py.exists():
            subprocess.Popen([sys.executable, str(app_py)], cwd=str(app_dir))
    except Exception as e:
        log(f"Không tự mở lại app được: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python tobo_update_helper.py <update.zip> <app_dir>")
        input("Press Enter...")
        return 1

    zip_path = Path(sys.argv[1]).resolve()
    app_dir = Path(sys.argv[2]).resolve()
    updates_dir = app_dir / "updates"
    staging = updates_dir / f"_apply_{int(time.time())}"

    try:
        log("TOBO VietSub Auto Updater")
        log("Đang chờ app chính đóng...")
        time.sleep(2)

        if not zip_path.exists():
            raise RuntimeError(f"Không thấy file cập nhật: {zip_path}")
        if not app_dir.exists():
            raise RuntimeError(f"Không thấy thư mục app: {app_dir}")

        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir(parents=True, exist_ok=True)

        log("Đang giải nén gói cập nhật...")
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(staging)

        src_root = find_source_root(staging)
        log(f"Nguồn cập nhật: {src_root}")
        log("Đang ghi đè file app mới...")
        copied = copy_update_files(src_root, app_dir)

        (updates_dir / "last_update.txt").write_text(
            f"Updated at {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Package: {zip_path}\n"
            f"Source: {src_root}\n"
            f"Copied files: {copied}\n"
            "Preserved: .venv, output, temp, updates, build, dist, release\n",
            encoding="utf-8"
        )

        shutil.rmtree(staging, ignore_errors=True)
        log(f"Hoàn tất. Đã cập nhật {copied} file.")
        log("Đang mở lại app...")
        restart_app(app_dir)
        time.sleep(2)
        return 0
    except Exception as e:
        log(f"LỖI CẬP NHẬT: {e}")
        input("Press Enter to close...")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
