# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

project_dir = Path('.').resolve()
asset_dir = project_dir / 'assets'
ffmpeg_dir = project_dir / 'ffmpeg'
helper_file = project_dir / 'tobo_update_helper.py'

datas = []
binaries = []
hiddenimports = []

for pkg in ['faster_whisper', 'ctranslate2', 'av', 'tokenizers', 'huggingface_hub', 'deep_translator']:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

if asset_dir.exists():
    datas.append((str(asset_dir), 'assets'))
if ffmpeg_dir.exists():
    datas.append((str(ffmpeg_dir), 'ffmpeg'))
if helper_file.exists():
    datas.append((str(helper_file), '.'))

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[str(project_dir)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TOBO_VietSub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(asset_dir / 'app_icon.ico') if (asset_dir / 'app_icon.ico').exists() else None,
)
