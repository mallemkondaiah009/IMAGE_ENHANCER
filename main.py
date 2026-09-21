"""
main.py — LUMIÈRE Fine Jewelry AI Studio
Application Bootstrap: All-in-One Luxury Studio Workspace
=========================================================
"""
import sys
import ctypes

# Enable Windows Per-Monitor High-DPI awareness to ensure razor-sharp rendering
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# Ensure UTF-8 console output on Windows or dummy stream if windowed
import os
import io

if sys.stdout is None:
    sys.stdout = io.StringIO()
elif hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

if sys.stderr is None:
    sys.stderr = io.StringIO()
elif hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Safeguard against PyInstaller missing package metadata (e.g. pymatting, rembg)
import importlib.metadata
_orig_metadata_version = importlib.metadata.version

def _safe_metadata_version(pkg_name: str) -> str:
    try:
        return _orig_metadata_version(pkg_name)
    except importlib.metadata.PackageNotFoundError:
        return "1.1.12"

importlib.metadata.version = _safe_metadata_version

import flet as ft
from app.config import settings
from app.theme import StudioColors
from app.viewmodels import StudioViewModel
from app.views import StudioView

# Configure permanent on-disk model directories for instant startup
user_u2net = os.path.join(os.path.expanduser("~"), ".u2net")
appdata_models = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "ImageStudio", "models")
if os.path.exists(os.path.join(user_u2net, "isnet-general-use.onnx")):
    os.environ["U2NET_HOME"] = user_u2net
elif os.path.exists(os.path.join(appdata_models, "isnet-general-use.onnx")):
    os.environ["U2NET_HOME"] = appdata_models
elif os.path.exists(os.path.join(settings.models_dir, "isnet-general-use.onnx")):
    os.environ["U2NET_HOME"] = settings.models_dir
else:
    os.environ.setdefault("U2NET_HOME", user_u2net)


async def main(page: ft.Page):
    # ── 1. Window & Stage Setup ───────────────────────────────────────────────
    page.title = "Image Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.theme = ft.Theme(font_family="Segoe UI")
    page.padding = 16
    page.spacing = 12

    if hasattr(page, "window"):
        page.window.width = 1380
        page.window.height = 880
        page.window.min_width = 1100
        page.window.min_height = 720
        await page.window.center()

    # ── 2. Unified All-in-One Studio Workspace (Zero Page Hopping) ────────────
    viewmodel = StudioViewModel()
    studio_view = StudioView(page=page, viewmodel=viewmodel)

    page.add(studio_view)


if __name__ == "__main__":
    print("=" * 62)
    print(f"  *  {settings.brand_name} {settings.brand_tagline}  v{settings.app_version}")
    print("  *  Launching Flet Desktop Application (All-in-One Studio)...")
    print("=" * 62)
    ft.run(main)
