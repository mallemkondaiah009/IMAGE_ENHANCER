"""
app/components/header_bar.py
Dark Obsidian Studio branding header with centered dual-mode switcher tabs (Enhance Image & Background Remover).
Right side text completely removed for ultra-clean symmetry and focus.
"""
from typing import Callable, Optional
import flet as ft
from app.config import settings
from app.models import EnhancementMode


class HeaderBar(ft.Container):
    def __init__(self, on_mode_change: Optional[Callable[[EnhancementMode], None]] = None):
        super().__init__()
        self._on_mode_change = on_mode_change
        self._active_mode = EnhancementMode.ENHANCE

        self.padding = ft.Padding.symmetric(horizontal=20, vertical=8)
        self.bgcolor = "#0B0F19"
        self.border = ft.Border.all(1.5, "#1E293B")
        self.border_radius = 4
        self.shadow = None

        # ── Mode Switcher Tabs (Centered, Minimal Luxury) ─────────────────────
        self.tab_enhance_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color="#FFFFFF", size=15)
        self.tab_enhance_text = ft.Text("Enhance Image", size=12, weight=ft.FontWeight.W_800, color="#FFFFFF")
        self.tab_enhance = ft.Container(
            content=ft.Row(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.tab_enhance_icon, self.tab_enhance_text],
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=["#2563EB", "#1D4ED8"],
            ),
            border_radius=4,
            padding=ft.Padding.symmetric(horizontal=24, vertical=8),
            shadow=None,
            on_click=lambda e: self._handle_tab_click(EnhancementMode.ENHANCE),
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        )

        self.tab_cutout_icon = ft.Icon(ft.Icons.CONTENT_CUT, color="#94A3B8", size=15)
        self.tab_cutout_text = ft.Text("Background Remover", size=12, weight=ft.FontWeight.W_700, color="#94A3B8")
        self.tab_cutout = ft.Container(
            content=ft.Row(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.tab_cutout_icon, self.tab_cutout_text],
            ),
            bgcolor=None,
            border_radius=4,
            padding=ft.Padding.symmetric(horizontal=24, vertical=8),
            shadow=None,
            on_click=lambda e: self._handle_tab_click(EnhancementMode.REMOVE_BG),
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        )

        mode_switcher = ft.Container(
            content=ft.Row(
                spacing=4,
                controls=[self.tab_enhance, self.tab_cutout],
            ),
            bgcolor="#05070D",
            border=ft.Border.all(1, "#1E293B"),
            border_radius=4,
            padding=3,
        )

        # ── Assemble Header (Clean Centered Mode Bar) ────────────────────────
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[mode_switcher],
        )

    def _handle_tab_click(self, mode: EnhancementMode) -> None:
        self.set_active_mode(mode)
        if self._on_mode_change:
            self._on_mode_change(mode)

    def set_active_mode(self, mode: EnhancementMode) -> None:
        self._active_mode = mode

        # ── Reset all tabs to inactive state ──────────────────────────────────
        for tab, icon, text in [
            (self.tab_enhance, self.tab_enhance_icon, self.tab_enhance_text),
            (self.tab_cutout, self.tab_cutout_icon, self.tab_cutout_text),
        ]:
            tab.gradient = None
            tab.bgcolor = None
            tab.shadow = None
            icon.color = "#94A3B8"
            text.color = "#94A3B8"
            text.weight = ft.FontWeight.W_700

        # ── Activate the selected tab ─────────────────────────────────────────
        if mode == EnhancementMode.ENHANCE:
            self.tab_enhance.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=["#2563EB", "#1D4ED8"],
            )
            self.tab_enhance.shadow = None
            self.tab_enhance_icon.color = "#FFFFFF"
            self.tab_enhance_text.color = "#FFFFFF"
            self.tab_enhance_text.weight = ft.FontWeight.W_800

        elif mode == EnhancementMode.REMOVE_BG:
            self.tab_cutout.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                colors=["#059669", "#047857"],
            )
            self.tab_cutout.shadow = None
            self.tab_cutout_icon.color = "#FFFFFF"
            self.tab_cutout_text.color = "#FFFFFF"
            self.tab_cutout_text.weight = ft.FontWeight.W_800

        try:
            if self.page:
                self.update()
        except Exception:
            pass
