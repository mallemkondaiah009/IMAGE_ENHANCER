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

        self.padding = ft.Padding.symmetric(horizontal=20, vertical=10)
        self.bgcolor = "#0B0F19"
        self.border = ft.Border.all(1.5, "#1E293B")
        self.border_radius = 16
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=18, color="#00000060", offset=ft.Offset(0, 4))

        # ── Left: Brand Identity ──────────────────────────────────────────────
        brand_icon = ft.Container(
            content=ft.Icon(ft.Icons.DIAMOND, color="#3B82F6", size=20),
            width=38,
            height=38,
            bgcolor="#161F30",
            border=ft.Border.all(1.5, "#1E293B"),
            border_radius=19,
            alignment=ft.Alignment(0, 0),
            shadow=ft.BoxShadow(blur_radius=8, color="#2563EB25", offset=ft.Offset(0, 2)),
        )

        brand_text = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    settings.brand_name.upper(),
                    size=18,
                    weight=ft.FontWeight.W_900,
                    color="#FFFFFF",
                ),
                ft.Container(
                    content=ft.Text("AI STUDIO", size=10, weight=ft.FontWeight.W_800, color="#60A5FA"),
                    bgcolor="#161F30",
                    border=ft.Border.all(1, "#1E293B"),
                    border_radius=10,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                ),
            ],
        )

        left_section = ft.Container(
            width=200,
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[brand_icon, brand_text],
            ),
        )

        # ── Center: Dual Mode Switcher Tabs ───────────────────────────────────
        self.tab_enhance_icon = ft.Icon(ft.Icons.AUTO_AWESOME, color="#FFFFFF", size=16)
        self.tab_enhance_text = ft.Text("Enhance Image", size=13, weight=ft.FontWeight.W_800, color="#FFFFFF")
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
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=20, vertical=9),
            shadow=ft.BoxShadow(blur_radius=12, color="#2563EB50", offset=ft.Offset(0, 3)),
            on_click=lambda e: self._handle_tab_click(EnhancementMode.ENHANCE),
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        )

        self.tab_cutout_icon = ft.Icon(ft.Icons.CONTENT_CUT, color="#94A3B8", size=16)
        self.tab_cutout_text = ft.Text("Background Remover", size=13, weight=ft.FontWeight.W_700, color="#94A3B8")
        self.tab_cutout = ft.Container(
            content=ft.Row(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.tab_cutout_icon, self.tab_cutout_text],
            ),
            bgcolor=None,
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=20, vertical=9),
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
            border_radius=24,
            padding=4,
        )

        # ── Right: Balanced Clean Margin (All Text Removed) ───────────────────
        right_section = ft.Container(
            width=200,
            alignment=ft.Alignment(1, 0),
        )

        # ── Assemble Header ───────────────────────────────────────────────────
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[left_section, mode_switcher, right_section],
        )

    def _handle_tab_click(self, mode: EnhancementMode) -> None:
        self.set_active_mode(mode)
        if self._on_mode_change:
            self._on_mode_change(mode)

    def set_active_mode(self, mode: EnhancementMode) -> None:
        self._active_mode = mode
        if mode == EnhancementMode.ENHANCE:
            # Activate Enhance Tab (Royal Sapphire Blue)
            self.tab_enhance.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=["#2563EB", "#1D4ED8"],
            )
            self.tab_enhance.bgcolor = None
            self.tab_enhance.shadow = ft.BoxShadow(blur_radius=12, color="#2563EB50", offset=ft.Offset(0, 3))
            self.tab_enhance_icon.color = "#FFFFFF"
            self.tab_enhance_text.color = "#FFFFFF"
            self.tab_enhance_text.weight = ft.FontWeight.W_800

            # Deactivate Cutout Tab
            self.tab_cutout.gradient = None
            self.tab_cutout.bgcolor = None
            self.tab_cutout.shadow = None
            self.tab_cutout_icon.color = "#94A3B8"
            self.tab_cutout_text.color = "#94A3B8"
            self.tab_cutout_text.weight = ft.FontWeight.W_700

        elif mode == EnhancementMode.REMOVE_BG:
            # Activate Cutout Tab (Emerald Green)
            self.tab_cutout.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=["#059669", "#047857"],
            )
            self.tab_cutout.bgcolor = None
            self.tab_cutout.shadow = ft.BoxShadow(blur_radius=12, color="#05966950", offset=ft.Offset(0, 3))
            self.tab_cutout_icon.color = "#FFFFFF"
            self.tab_cutout_text.color = "#FFFFFF"
            self.tab_cutout_text.weight = ft.FontWeight.W_800

            # Deactivate Enhance Tab
            self.tab_enhance.gradient = None
            self.tab_enhance.bgcolor = None
            self.tab_enhance.shadow = None
            self.tab_enhance_icon.color = "#94A3B8"
            self.tab_enhance_text.color = "#94A3B8"
            self.tab_enhance_text.weight = ft.FontWeight.W_700

        try:
            if self.page:
                self.update()
        except Exception:
            pass
