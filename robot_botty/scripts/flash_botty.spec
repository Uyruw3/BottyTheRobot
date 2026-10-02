# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec — compila flash_botty.py a .exe
#
# Uso:
#   pyinstaller scripts\flash_botty.spec
#

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Collect all data files to embed
datas = []

# Add botty package
for f in (PROJECT_ROOT / "botty").rglob("*"):
    if f.is_file() and f.suffix not in (".pyc",):
        rel = f.relative_to(PROJECT_ROOT)
        datas.append((str(f), str(rel.parent)))

# Add scripts
for f in (PROJECT_ROOT / "scripts").glob("*"):
    if f.is_file() and f.suffix not in (".pyc", ".spec"):
        rel = f.relative_to(PROJECT_ROOT)
        datas.append((str(f), str(rel.parent)))

# Add root files
for name in ("pyproject.toml", "requirements.txt"):
    f = PROJECT_ROOT / name
    if f.exists():
        datas.append((str(f), "."))

block_cipher = None

a = Analysis(
    [str(PROJECT_ROOT / "scripts" / "flash_botty.py")],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=["paramiko"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="flash_botty",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
