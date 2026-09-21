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

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import flet as ft
from app.config import settings
from app.theme import StudioColors
from app.viewmodels import StudioViewModel
from app.views import StudioView


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
