"""
app/views/home_view.py
Pure, ultra-clean luxury dashboard featuring only the two visual showcase cards
with full jewelry visibility and floating action buttons — header, under-text,
and footer completely removed for maximum clarity and focus.
"""
from typing import Callable
import flet as ft
from app.theme import StudioColors, StudioStyles
from app.components import AnimatedButton


class HomeView(ft.Container):
    def __init__(
        self,
        on_select_enhance: Callable[[], None],
        on_select_remove_bg: Callable[[], None],
    ):
        super().__init__()
        self.expand = True
        self._on_select_enhance = on_select_enhance
        self._on_select_remove_bg = on_select_remove_bg
        self.bgcolor = StudioColors.BG_WHITE

        # ── Card 1: Enhance Image (Royal Sapphire Theme - Blue Background Fill) ──
        preview_enhance_banner = ft.Container(
            content=ft.Image(
                src="assets/preview_diamond.jpg",
                fit=ft.BoxFit.CONTAIN,
                height=220,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding.symmetric(vertical=8, horizontal=10),
            border=ft.Border.all(1.5, "#BFDBFE"),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=12, color="#1E3A8A14", offset=ft.Offset(0, 3)),
            height=230,
        )

        btn_enhance_action = AnimatedButton(
            text="OPEN ENHANCE STUDIO",
            icon=ft.Icons.ARROW_FORWARD,
            gradient_colors=["#2563EB", "#1D4ED8"],
            hover_gradient_colors=["#3B82F6", "#2563EB"],
            glow_color="#2563EB66",
            height=46,
            font_size=13,
            border_radius=23,
            padding=ft.Padding.symmetric(vertical=10, horizontal=30),
            on_click=lambda e: self._on_select_enhance(),
        )

        card_enhance = ft.Container(
            content=ft.Column(
                spacing=14,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.AUTO_AWESOME, color="#2563EB", size=22),
                                                width=42,
                                                height=42,
                                                bgcolor="#FFFFFF",
                                                border=ft.Border.all(1.5, "#93C5FD"),
                                                border_radius=21,
                                                alignment=ft.Alignment(0, 0),
                                                shadow=ft.BoxShadow(blur_radius=8, color="#2563EB18", offset=ft.Offset(0, 2)),
                                            ),
                                            ft.Text(
                                                "Enhance Image",
                                                size=22,
                                                weight=ft.FontWeight.W_800,
                                                color=StudioColors.TEXT_PRIMARY,
                                            ),
                                        ],
                                    ),
                                    ft.Container(
                                        content=ft.Text("4X VULKAN ENGINE", size=10, weight=ft.FontWeight.W_800, color="#1D4ED8"),
                                        bgcolor="#FFFFFF",
                                        border=ft.Border.all(1, "#93C5FD"),
                                        border_radius=14,
                                        padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                                    ),
                                ],
                            ),
                            ft.Text(
                                "4x Super-resolution polishing diamond facet fire and gold specular reflections with color-locked clarity.",
                                size=12,
                                color="#334155",
                            ),
                            preview_enhance_banner,
                            ft.Row(
                                wrap=True,
                                spacing=6,
                                controls=[
                                    self._build_color_badge("4x Super-Resolution", "#FFFFFF", "#93C5FD", "#1D4ED8"),
                                    self._build_color_badge("Exact 2000×2000 px", "#FFFFFF", "#93C5FD", "#1D4ED8"),
                                    self._build_color_badge("Master Studio Quality", "#FFFFFF", "#93C5FD", "#1D4ED8"),
                                    self._build_color_badge("Zero Color Bleeding", "#FFFFFF", "#93C5FD", "#1D4ED8"),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[btn_enhance_action],
                    ),
                ],
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#F0F7FF", "#DBEAFE"],
            ),
            border=ft.Border.all(1.5, "#93C5FD"),
            border_radius=20,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=26, color="#2563EB20", offset=ft.Offset(0, 8)),
            padding=24,
            expand=1,
            on_click=lambda e: self._on_select_enhance(),
        )

        # ── Card 2: Remove Background (Emerald Jade Theme - Green Background Fill) ─
        preview_cutout_banner = ft.Container(
            content=ft.Image(
                src="assets/preview_emerald.jpg",
                fit=ft.BoxFit.CONTAIN,
                height=220,
            ),
            bgcolor="#FFFFFF",
            border_radius=14,
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding.symmetric(vertical=8, horizontal=10),
            border=ft.Border.all(1.5, "#A7F3D0"),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=12, color="#05966914", offset=ft.Offset(0, 3)),
            height=230,
        )

        btn_remove_bg_action = AnimatedButton(
            text="OPEN CUTOUT STUDIO",
            icon=ft.Icons.ARROW_FORWARD,
            gradient_colors=["#059669", "#047857"],
            hover_gradient_colors=["#10B981", "#059669"],
            glow_color="#05966966",
            height=46,
            font_size=13,
            border_radius=23,
            padding=ft.Padding.symmetric(vertical=10, horizontal=30),
            on_click=lambda e: self._on_select_remove_bg(),
        )

        card_remove_bg = ft.Container(
            content=ft.Column(
                spacing=14,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.CONTENT_CUT, color="#059669", size=22),
                                                width=42,
                                                height=42,
                                                bgcolor="#FFFFFF",
                                                border=ft.Border.all(1.5, "#6EE7B7"),
                                                border_radius=21,
                                                alignment=ft.Alignment(0, 0),
                                                shadow=ft.BoxShadow(blur_radius=8, color="#05966918", offset=ft.Offset(0, 2)),
                                            ),
                                            ft.Text(
                                                "Remove Background",
                                                size=22,
                                                weight=ft.FontWeight.W_800,
                                                color=StudioColors.TEXT_PRIMARY,
                                            ),
                                        ],
                                    ),
                                    ft.Container(
                                        content=ft.Text("AI BIREFNET CUTOUT", size=10, weight=ft.FontWeight.W_800, color="#047857"),
                                        bgcolor="#FFFFFF",
                                        border=ft.Border.all(1, "#6EE7B7"),
                                        border_radius=14,
                                        padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                                    ),
                                ],
                            ),
                            ft.Text(
                                "Isolate gemstone solitaires, rings, and settings using BiRefNet / U2Net AI models into transparent PNGs.",
                                size=12,
                                color="#334155",
                            ),
                            preview_cutout_banner,
                            ft.Row(
                                wrap=True,
                                spacing=6,
                                controls=[
                                    self._build_color_badge("BiRefNet AI Cutout", "#FFFFFF", "#6EE7B7", "#047857"),
                                    self._build_color_badge("Studio White / Transparent", "#FFFFFF", "#6EE7B7", "#047857"),
                                    self._build_color_badge("Exact 2000×2000 px", "#FFFFFF", "#6EE7B7", "#047857"),
                                    self._build_color_badge("Master Studio Quality", "#FFFFFF", "#6EE7B7", "#047857"),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[btn_remove_bg_action],
                    ),
                ],
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#ECFDF5", "#D1FAE5"],
            ),
            border=ft.Border.all(1.5, "#6EE7B7"),
            border_radius=20,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=26, color="#05966920", offset=ft.Offset(0, 8)),
            padding=24,
            expand=1,
            on_click=lambda e: self._on_select_remove_bg(),
        )

        # ── Interactive Micro-Animations ───────────────────────────────────────
        def on_enhance_hover(e):
            is_h = e.data == "true"
            card_enhance.scale = 1.012 if is_h else 1.0
            card_enhance.border = ft.Border.all(2, "#2563EB" if is_h else "#93C5FD")
            card_enhance.shadow = ft.BoxShadow(
                spread_radius=1 if is_h else 0,
                blur_radius=32 if is_h else 26,
                color="#2563EB35" if is_h else "#2563EB20",
                offset=ft.Offset(0, 10 if is_h else 8),
            )
            card_enhance.update()

        def on_remove_bg_hover(e):
            is_h = e.data == "true"
            card_remove_bg.scale = 1.012 if is_h else 1.0
            card_remove_bg.border = ft.Border.all(2, "#059669" if is_h else "#6EE7B7")
            card_remove_bg.shadow = ft.BoxShadow(
                spread_radius=1 if is_h else 0,
                blur_radius=32 if is_h else 26,
                color="#05966935" if is_h else "#05966920",
                offset=ft.Offset(0, 10 if is_h else 8),
            )
            card_remove_bg.update()

        card_enhance.scale = 1.0
        card_enhance.animate = ft.Animation(220, ft.AnimationCurve.EASE_OUT)
        card_enhance.animate_scale = ft.Animation(200, ft.AnimationCurve.EASE_OUT_CUBIC)
        card_enhance.on_hover = on_enhance_hover
        card_enhance.mouse_cursor = ft.MouseCursor.CLICK

        card_remove_bg.scale = 1.0
        card_remove_bg.animate = ft.Animation(220, ft.AnimationCurve.EASE_OUT)
        card_remove_bg.animate_scale = ft.Animation(200, ft.AnimationCurve.EASE_OUT_CUBIC)
        card_remove_bg.on_hover = on_remove_bg_hover
        card_remove_bg.mouse_cursor = ft.MouseCursor.CLICK

        cards_row = ft.Row(
            spacing=24,
            controls=[card_enhance, card_remove_bg],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # ── Ultra-Clean Layout: Only the Two Visual Cards ─────────────────────
        self.content = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[cards_row],
                expand=True,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
            padding=ft.Padding.symmetric(horizontal=12, vertical=12),
        )

    def _build_color_badge(self, text: str, bgcolor: str, border_color: str, text_color: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(text, size=10, color=text_color, weight=ft.FontWeight.W_700),
            bgcolor=bgcolor,
            border=ft.Border.all(1, border_color),
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )
