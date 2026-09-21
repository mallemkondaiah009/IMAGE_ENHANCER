"""
app/components/comparison_canvas.py
Interactive Before/After Comparison Slider with draggable vertical divider.
Shows original image on the left and enhanced result on the right,
with a premium glowing slider control for smooth drag interaction.
"""
import os
from typing import Callable, Optional
import flet as ft
from app.models import StudioState, ViewMode, EnhancementMode, CutoutBackground
from app.theme import StudioColors, StudioStyles
from .animated_button import AnimatedButton


class ComparisonCanvas(ft.Container):
    def __init__(
        self,
        on_save_click: Callable[[], None],
        on_view_change: Optional[Callable[[ViewMode], None]] = None,
        on_hold_toggle: Optional[Callable[[], None]] = None,
        on_cutout_bg_change: Optional[Callable[[CutoutBackground], None]] = None,
    ):
        super().__init__()
        self._on_save_click = on_save_click
        self._on_cutout_bg_change = on_cutout_bg_change
        self._slider_pct = 50  # 0 = full before, 100 = full after

        self.bgcolor = StudioColors.CARD_BG
        self.border = ft.Border.all(1.5, StudioColors.CARD_BORDER)
        self.border_radius = StudioStyles.RADIUS_CARD
        self.padding = 18
        self.expand = True

        # ── 1. Toolbar: Title on Left, Background Switcher, Download Button on Right ───
        self.canvas_title = ft.Text(
            "IMAGE INSPECTION CANVAS",
            size=12,
            weight=ft.FontWeight.W_800,
            color=StudioColors.TEXT_PRIMARY,
        )

        self.canvas_badge = ft.Container(
            content=ft.Text("IDLE", size=10, weight=ft.FontWeight.W_800, color=StudioColors.TEXT_MUTED),
            bgcolor=StudioColors.SURFACE_MUTED,
            border=ft.Border.all(1, StudioColors.CARD_BORDER),
            border_radius=2,
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
        )

        # Background switcher chips (BG White vs BG Black vs Transparent)
        self.btn_bg_white_text = ft.Text("BG White", size=11, weight=ft.FontWeight.W_800, color="#FFFFFF")
        self.btn_bg_white_icon = ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color="#FFFFFF", size=13)
        self.btn_bg_white = ft.Container(
            content=ft.Row(
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.btn_bg_white_icon, self.btn_bg_white_text],
            ),
            bgcolor="#059669",
            border_radius=2,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            on_click=lambda e: self._handle_bg_click(CutoutBackground.WHITE),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

        self.btn_bg_black_text = ft.Text("BG Black", size=11, weight=ft.FontWeight.W_700, color="#94A3B8")
        self.btn_bg_black_icon = ft.Icon(ft.Icons.NIGHTLIGHT_ROUND, color="#94A3B8", size=13)
        self.btn_bg_black = ft.Container(
            content=ft.Row(
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.btn_bg_black_icon, self.btn_bg_black_text],
            ),
            bgcolor=None,
            border_radius=2,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            on_click=lambda e: self._handle_bg_click(CutoutBackground.BLACK),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

        self.btn_bg_transparent_text = ft.Text("Transparent", size=11, weight=ft.FontWeight.W_700, color="#94A3B8")
        self.btn_bg_transparent_icon = ft.Icon(ft.Icons.GRID_VIEW_ROUNDED, color="#94A3B8", size=13)
        self.btn_bg_transparent = ft.Container(
            content=ft.Row(
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.btn_bg_transparent_icon, self.btn_bg_transparent_text],
            ),
            bgcolor=None,
            border_radius=2,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            on_click=lambda e: self._handle_bg_click(CutoutBackground.TRANSPARENT),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

        self.bg_switcher = ft.Container(
            content=ft.Row(
                spacing=3,
                controls=[self.btn_bg_white, self.btn_bg_black, self.btn_bg_transparent],
            ),
            bgcolor="#05070D",
            border=ft.Border.all(1, "#1E293B"),
            border_radius=4,
            padding=3,
            visible=False,
        )

        # Prominent Animated Download Button (Floating Pill)
        self.btn_download = AnimatedButton(
            text="Download",
            icon=ft.Icons.DOWNLOAD,
            gradient_colors=["#059669", "#047857"],
            hover_gradient_colors=["#10B981", "#059669"],
            glow_color="#05966955",
            height=38,
            font_size=12,
            border_radius=4,
            padding=ft.Padding.symmetric(vertical=8, horizontal=18),
            disabled=True,
            on_click=lambda e: self._on_save_click(),
        )

        toolbar = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=10, controls=[self.canvas_title, self.canvas_badge]),
                    self.bg_switcher,
                    self.btn_download,
                ],
            ),
            border=ft.Border(bottom=ft.BorderSide(1, StudioColors.CARD_BORDER)),
            padding=ft.Padding.only(bottom=12),
        )

        # ── 2. Views ──────────────────────────────────────────────────────────
        # Empty State
        self.empty_state = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED, color=StudioColors.GOLD_PRIMARY, size=46),
                        width=88,
                        height=88,
                        bgcolor=StudioColors.GOLD_CHIP_BG,
                        border=ft.Border.all(1.5, StudioColors.GOLD_CHIP_BORDER),
                        border_radius=4,
                        alignment=ft.Alignment(0, 0),
                        shadow=None,
                    ),
                    ft.Text("Studio Canvas Idle", size=18, weight=ft.FontWeight.W_800, color=StudioColors.TEXT_PRIMARY),
                    ft.Container(
                        content=ft.Text(
                            "Select a single photo or an entire image folder to begin.\n"
                            "Supports JPG, JPEG, PNG, and WebP formats.",
                            size=12,
                            color=StudioColors.TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        width=440,
                    ),
                ],
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
        )

        # Single Full Image Display Box (clean studio canvas display)
        self.main_img = ft.Image(src="", fit=ft.BoxFit.CONTAIN, border_radius=2)
        self.single_display_box = ft.Container(
            content=self.main_img,
            bgcolor=StudioColors.CANVAS_BG,
            border=ft.Border.all(1.5, StudioColors.CARD_BORDER),
            border_radius=4,
            shadow=None,
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=16,
            visible=False,
        )

        # ── High-Tech AI Holographic HUD Processing Overlay ───────────────────
        self.hud_scan_line = ft.Container(
            height=2,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=["#3B82F600", "#60A5FA", "#93C5FD", "#60A5FA", "#3B82F600"],
            ),
            border_radius=1,
        )

        self.hud_ring = ft.ProgressRing(
            width=64,
            height=64,
            stroke_width=3.5,
            color="#3B82F6",
            bgcolor="#1E293B55",
        )
        self.hud_icon = ft.Icon(
            ft.Icons.AUTO_AWESOME,
            size=26,
            color="#60A5FA",
        )
        self.hud_core_glow = ft.Container(
            content=ft.Stack(
                alignment=ft.Alignment(0, 0),
                controls=[
                    self.hud_ring,
                    self.hud_icon,
                ],
            ),
            width=68,
            height=68,
            alignment=ft.Alignment(0, 0),
        )

        self.hud_badge_icon = ft.Icon(ft.Icons.BOLT, size=12, color="#60A5FA")
        self.hud_badge_text = ft.Text(
            "REAL-ESRGAN VULKAN 4X",
            size=10,
            weight=ft.FontWeight.W_800,
            color="#60A5FA",
        )
        self.hud_badge = ft.Container(
            content=ft.Row(
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[self.hud_badge_icon, self.hud_badge_text],
            ),
            bgcolor="#1E293B88",
            border=ft.Border.all(1, "#3B82F666"),
            border_radius=2,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )

        self.loading_step = ft.Text(
            "Processing AI Workflow...",
            size=15,
            weight=ft.FontWeight.W_800,
            color="#F8FAFC",
            text_align=ft.TextAlign.CENTER,
        )
        self.loading_sub = ft.Text(
            "Executing engine...",
            size=11,
            color="#94A3B8",
            text_align=ft.TextAlign.CENTER,
        )

        self.batch_progress_text = ft.Text("Batch Progress: 0/0", size=11, weight=ft.FontWeight.W_700, color="#60A5FA")
        self.batch_progress_bar = ft.ProgressBar(
            width=320,
            height=4,
            value=0,
            color="#3B82F6",
            bgcolor="#1E293B",
            border_radius=2,
        )
        self.batch_progress_container = ft.Container(
            content=ft.Column(
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.batch_progress_text,
                    self.batch_progress_bar,
                ],
            ),
            visible=False,
        )

        self.telemetry_left_icon = ft.Icon(ft.Icons.ASPECT_RATIO, size=12, color="#64748B")
        self.telemetry_left_text = ft.Text("2000×2000 RESOLUTION", size=10, weight=ft.FontWeight.W_700, color="#94A3B8")
        self.telemetry_right_icon = ft.Icon(ft.Icons.MEMORY, size=12, color="#64748B")
        self.telemetry_right_text = ft.Text("VULKAN ACCELERATED", size=10, weight=ft.FontWeight.W_700, color="#94A3B8")

        self.telemetry_row = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    ft.Row(spacing=4, controls=[self.telemetry_left_icon, self.telemetry_left_text]),
                    ft.Container(width=1, height=10, bgcolor="#334155"),
                    ft.Row(spacing=4, controls=[self.telemetry_right_icon, self.telemetry_right_text]),
                ],
            ),
            border=ft.Border(top=ft.BorderSide(1, "#1E293B")),
            padding=ft.Padding.only(top=10),
        )

        self.hud_card = ft.Container(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    self.hud_scan_line,
                    self.hud_core_glow,
                    self.hud_badge,
                    self.loading_step,
                    self.loading_sub,
                    self.batch_progress_container,
                    self.telemetry_row,
                ],
            ),
            width=420,
            bgcolor="#070B14EE",
            border=ft.Border.all(1.5, "#2563EB66"),
            border_radius=4,
            padding=ft.Padding.symmetric(vertical=20, horizontal=22),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=28, color="#000000BB", offset=ft.Offset(0, 8)),
        )

        self.loading_overlay = ft.Container(
            content=self.hud_card,
            alignment=ft.Alignment(0, 0),
            bgcolor=StudioColors.CANVAS_BG,
            border=ft.Border.all(1.5, StudioColors.CARD_BORDER),
            border_radius=4,
            expand=True,
            visible=False,
        )

        self.view_stack = ft.Stack(
            controls=[
                self.empty_state,
                self.single_display_box,
                self.loading_overlay,
            ],
            expand=True,
        )

        self.content = ft.Column(
            spacing=10,
            controls=[
                toolbar,
                self.view_stack,
            ],
            expand=True,
        )

    def _handle_bg_click(self, bg: CutoutBackground) -> None:
        """Forward background switcher click to callback."""
        if self._on_cutout_bg_change:
            self._on_cutout_bg_change(bg)

    # ── State Update ──────────────────────────────────────────────────────────
    def update_from_state(self, state: StudioState) -> None:
        if state.is_batch:
            self.btn_download.update_appearance(
                text="Download Full Folder",
                icon=ft.Icons.DRIVE_FOLDER_UPLOAD,
                gradient_colors=["#059669", "#047857"],
                hover_gradient_colors=["#10B981", "#059669"],
                glow_color="#05966955",
            )
            self.btn_download.disabled = (
                state.batch_output_dir is None
                or not os.path.exists(state.batch_output_dir)
                or state.is_processing
            )
        else:
            self.btn_download.update_appearance(
                text="Download",
                icon=ft.Icons.DOWNLOAD,
                gradient_colors=["#059669", "#047857"],
                hover_gradient_colors=["#10B981", "#059669"],
                glow_color="#05966955",
            )
            self.btn_download.disabled = state.output_path is None or state.is_processing

        is_bg_remover = (state.active_mode == EnhancementMode.REMOVE_BG)

        # Background switcher chip visibility and active state
        self.bg_switcher.visible = is_bg_remover and not state.is_processing
        if is_bg_remover:
            # Reset chip styles
            for btn, icon, text in [
                (self.btn_bg_white, self.btn_bg_white_icon, self.btn_bg_white_text),
                (self.btn_bg_black, self.btn_bg_black_icon, self.btn_bg_black_text),
                (self.btn_bg_transparent, self.btn_bg_transparent_icon, self.btn_bg_transparent_text),
            ]:
                btn.bgcolor = None
                icon.color = "#94A3B8"
                text.color = "#94A3B8"
                text.weight = ft.FontWeight.W_700

            if state.cutout_bg == CutoutBackground.WHITE:
                self.btn_bg_white.bgcolor = "#059669"
                self.btn_bg_white_icon.color = "#FFFFFF"
                self.btn_bg_white_text.color = "#FFFFFF"
                self.btn_bg_white_text.weight = ft.FontWeight.W_800
            elif state.cutout_bg == CutoutBackground.BLACK:
                self.btn_bg_black.bgcolor = "#2563EB"
                self.btn_bg_black_icon.color = "#FFFFFF"
                self.btn_bg_black_text.color = "#FFFFFF"
                self.btn_bg_black_text.weight = ft.FontWeight.W_800
            else:
                self.btn_bg_transparent.bgcolor = "#059669"
                self.btn_bg_transparent_icon.color = "#FFFFFF"
                self.btn_bg_transparent_text.color = "#FFFFFF"
                self.btn_bg_transparent_text.weight = ft.FontWeight.W_800

        # 1. Processing state
        if state.is_processing:
            self.loading_overlay.visible = True
            self.empty_state.visible = False
            self.single_display_box.visible = False

            self.loading_step.value = state.status_step or "Processing AI Workflow..."
            self.loading_sub.value = state.status_subtext or "Executing engine..."

            # Mode-specific HUD visual effects & styling
            if state.active_mode == EnhancementMode.ENHANCE:
                self.canvas_title.value = "AI SUPER-RESOLUTION SYNTHESIS IN PROGRESS"
                self.canvas_title.color = "#60A5FA"
                # 4x Super-Resolution Theme (Deep Sapphire Electric Blue)
                self.hud_ring.color = "#3B82F6"
                self.hud_icon.name = ft.Icons.AUTO_AWESOME
                self.hud_icon.color = "#60A5FA"
                self.hud_card.border = ft.Border.all(1.5, "#2563EB88")
                self.hud_scan_line.gradient = ft.LinearGradient(
                    begin=ft.Alignment(-1, 0),
                    end=ft.Alignment(1, 0),
                    colors=["#3B82F600", "#60A5FA", "#93C5FD", "#60A5FA", "#3B82F600"],
                )
                self.hud_badge_icon.name = ft.Icons.BOLT
                self.hud_badge_icon.color = "#60A5FA"
                self.hud_badge_text.value = "REAL-ESRGAN VULKAN 4X"
                self.hud_badge_text.color = "#60A5FA"
                self.hud_badge.border = ft.Border.all(1, "#3B82F666")
                self.hud_badge.bgcolor = "#1E293B88"
                self.telemetry_left_icon.name = ft.Icons.ASPECT_RATIO
                self.telemetry_left_text.value = "2000×2000 NATIVE"
                self.telemetry_right_icon.name = ft.Icons.MEMORY
                self.telemetry_right_text.value = "VULKAN GPU TENSOR"
                self.canvas_badge.content.value = "4X ENHANCING..."
                self.canvas_badge.content.color = "#60A5FA"
                self.canvas_badge.border = ft.Border.all(1, "#2563EB")
            else:
                self.canvas_title.value = "AI BACKGROUND CUTOUT IN PROGRESS"
                self.canvas_title.color = "#34D399"
                # Background Removal Theme (Emerald Laser Mint)
                self.hud_ring.color = "#10B981"
                self.hud_icon.name = ft.Icons.CONTENT_CUT
                self.hud_icon.color = "#34D399"
                self.hud_card.border = ft.Border.all(1.5, "#05966988")
                self.hud_scan_line.gradient = ft.LinearGradient(
                    begin=ft.Alignment(-1, 0),
                    end=ft.Alignment(1, 0),
                    colors=["#05966900", "#10B981", "#6EE7B7", "#10B981", "#05966900"],
                )
                self.hud_badge_icon.name = ft.Icons.AUTO_AWESOME_MOTION if state.is_batch else ft.Icons.SHIELD_OUTLINED
                self.hud_badge_icon.color = "#34D399"
                self.hud_badge_text.value = "BIREFNET / ISNET AI MATTING"
                self.hud_badge_text.color = "#34D399"
                self.hud_badge.border = ft.Border.all(1, "#05966966")
                self.hud_badge.bgcolor = "#064E3B44"
                self.telemetry_left_icon.name = ft.Icons.GRID_VIEW_ROUNDED
                self.telemetry_left_text.value = "ALPHA CUTOUT (32-BIT)"
                self.telemetry_right_icon.name = ft.Icons.AUTO_FIX_HIGH
                self.telemetry_right_text.value = "EDGE MATTING ACTIVE"
                self.canvas_badge.content.value = "REMOVING BG..."
                self.canvas_badge.content.color = "#34D399"
                self.canvas_badge.border = ft.Border.all(1, "#059669")

            # Batch Progress Tracker
            if state.is_batch and state.batch_total > 0:
                self.batch_progress_container.visible = True
                curr = state.batch_current_index
                tot = state.batch_total
                self.batch_progress_bar.value = curr / max(tot, 1)
                self.batch_progress_text.value = f"Processing [{curr}/{tot} Images]"
                self.batch_progress_bar.color = "#60A5FA" if state.active_mode == EnhancementMode.ENHANCE else "#34D399"
            else:
                self.batch_progress_container.visible = False

            return

        self.loading_overlay.visible = False

        # 2. Empty state (No image loaded)
        if not state.input_data_uri and not state.output_data_uri:
            self.empty_state.visible = True
            self.single_display_box.visible = False
            self.canvas_title.value = "IMAGE INSPECTION CANVAS"
            self.canvas_title.color = StudioColors.TEXT_PRIMARY
            self.canvas_badge.content.value = "IDLE"
            self.canvas_badge.content.color = StudioColors.TEXT_MUTED
            self.canvas_badge.border = ft.Border.all(1, StudioColors.CARD_BORDER)
            return

        self.empty_state.visible = False
        self.single_display_box.visible = True

        if state.output_data_uri:
            self.main_img.src = state.output_data_uri
            if is_bg_remover:
                if state.cutout_bg == CutoutBackground.WHITE:
                    self.canvas_title.value = "STUDIO WHITE BACKGROUND (2000×2000)"
                    self.canvas_title.color = "#34D399"
                    self.canvas_badge.content.value = "BG WHITE (#FFFFFF)"
                    self.canvas_badge.content.color = "#059669"
                    self.canvas_badge.border = ft.Border.all(1, "#059669")
                    self.single_display_box.border = ft.Border.all(1.5, "#059669")
                    self.single_display_box.bgcolor = "#FFFFFF"
                    self.single_display_box.image = None
                elif state.cutout_bg == CutoutBackground.BLACK:
                    self.canvas_title.value = "STUDIO BLACK BACKGROUND (2000×2000)"
                    self.canvas_title.color = "#60A5FA"
                    self.canvas_badge.content.value = "BG BLACK (#000000)"
                    self.canvas_badge.content.color = "#3B82F6"
                    self.canvas_badge.border = ft.Border.all(1, "#3B82F6")
                    self.single_display_box.border = ft.Border.all(1.5, "#3B82F6")
                    self.single_display_box.bgcolor = "#000000"
                    self.single_display_box.image = None
                else:
                    self.canvas_title.value = "TRANSPARENT CUTOUT (2000×2000)"
                    self.canvas_title.color = "#34D399"
                    self.canvas_badge.content.value = "TRANSPARENT PNG"
                    self.canvas_badge.content.color = "#10B981"
                    self.canvas_badge.border = ft.Border.all(1, "#059669")
                    self.single_display_box.border = ft.Border.all(1.5, "#059669")
                    self.single_display_box.bgcolor = "#0F172A"
                    self.single_display_box.image = None
            else:
                self.canvas_title.value = "4X SUPER-RESOLUTION RESULT"
                self.canvas_title.color = "#60A5FA"
                self.canvas_badge.content.value = "2000×2000 MASTER"
                self.canvas_badge.content.color = "#3B82F6"
                self.canvas_badge.border = ft.Border.all(1, "#3B82F6")
                self.single_display_box.border = ft.Border.all(1.5, "#3B82F6")
                self.single_display_box.bgcolor = StudioColors.CANVAS_BG
                self.single_display_box.image = None
        else:
            self.main_img.src = state.input_data_uri
            self.canvas_title.value = "SELECTED IMAGE (ORIGINAL)"
            self.canvas_title.color = StudioColors.TEXT_PRIMARY
            w = state.metrics.original_width
            h = state.metrics.original_height
            self.canvas_badge.content.value = f"{w} × {h} PX"
            self.canvas_badge.content.color = StudioColors.TEXT_SECONDARY
            self.canvas_badge.border = ft.Border.all(1, StudioColors.CARD_BORDER)
            self.single_display_box.border = ft.Border.all(1.5, StudioColors.CARD_BORDER)
            self.single_display_box.bgcolor = StudioColors.CANVAS_BG
            self.single_display_box.image = None
