# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all, copy_metadata

# ── 1. Base Data & Binary Files ───────────────────────────────────────────────
# AI models and Vulkan binaries are permanently stored on disk (%LOCALAPPDATA% & ~/.u2net)
# for instant (< 2s) application startup without decompressing 400MB on every launch.
datas = []
binaries = []
hiddenimports = [
    'rembg',
    'rembg.sessions',
    'rembg.sessions.base',
    'rembg.sessions.dis_general_use',
    'rembg.sessions.birefnet_general',
    'rembg.sessions.birefnet_general_lite',
    'rembg.sessions.birefnet_portrait',
    'rembg.sessions.birefnet_dis',
    'rembg.sessions.u2net',
    'rembg.sessions.u2netp',
    'rembg.sessions.silueta',
    'onnxruntime',
    'onnxruntime.capi',
    'onnxruntime.capi._pybind_state',
    'onnxruntime.capi.onnxruntime_pybind11_state',
    'pymatting',
    'pymatting.alpha',
    'pymatting.alpha.estimate_alpha_cf',
    'pymatting.foreground',
    'pymatting.foreground.estimate_foreground_ml',
    'pymatting.util',
    'scipy',
    'scipy.special',
    'scipy.special.cython_special',
    'scipy.spatial.transform._rotation_groups',
    'pooch',
    'PIL',
    'PIL.Image',
    'PIL.ImageFilter',
    'flet',
    'flet_desktop',
]

# ── 2. Collect Dynamic Libraries & Submodules for AI Toolchains ───────────────
for pkg in ['onnxruntime', 'rembg', 'pymatting']:
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

# ── 3. Copy Distribution Metadata (version, requirements) ─────────────────────
for pkg in ['rembg', 'pymatting', 'onnxruntime', 'tqdm', 'pooch', 'flet']:
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass

# ── 4. Analysis ───────────────────────────────────────────────────────────────
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# ── 5. Single Portable Executable ─────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ImageStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # Crucial: UPX corrupts onnxruntime.dll and C++ DLL entrypoints
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
