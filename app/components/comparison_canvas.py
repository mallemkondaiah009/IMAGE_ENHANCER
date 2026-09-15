"""
app/components/comparison_canvas.py
Clean, full-canvas inspection workspace displaying loaded and processed images.
Shows the selected image fully without split clutter, with a prominent Download Image button.
"""
from typing import Callable, Optional
import flet as ft
from app.models import StudioState, ViewMode, EnhancementMode
from app.theme import StudioColors, StudioStyles
from .animated_button import AnimatedButton


class ComparisonCanvas(ft.Container):
    def __init__(
        self,
        on_save_click: Callable[[], None],
        on_view_change: Optional[Callable[[ViewMode], None]] = None,
        on_hold_toggle: Optional[Callable[[], None]] = None,
    ):
        super().__init__()
        self._on_save_click = on_save_click

        self.bgcolor = StudioColors.CARD_BG
        self.border = ft.Border.all(1.5, StudioColors.CARD_BORDER)
        self.border_radius = StudioStyles.RADIUS_CARD
        self.padding = 18
        self.expand = True

        # ── 1. Toolbar: Title on Left, Download Button on Right ───────────────
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
            border_radius=12,
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        )

        # Prominent Animated Download Button (Floating Pill)
        self.btn_download = AnimatedButton(
            text="Download Image",
            icon=ft.Icons.DOWNLOAD,
            gradient_colors=["#059669", "#047857"],
            hover_gradient_colors=["#10B981", "#059669"],
            glow_color="#05966955",
            height=42,
            font_size=12,
            border_radius=21,
            padding=ft.Padding.symmetric(vertical=8, horizontal=22),
            disabled=True,
            on_click=lambda e: self._on_save_click(),
        )

        toolbar = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=10, controls=[self.canvas_title, self.canvas_badge]),
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
                        border_radius=44,
                        alignment=ft.Alignment(0, 0),
                        shadow=ft.BoxShadow(blur_radius=14, color="#2563EB20", offset=ft.Offset(0, 4)),
                    ),
                    ft.Text("Studio Canvas Idle", size=18, weight=ft.FontWeight.W_800, color=StudioColors.TEXT_PRIMARY),
                    ft.Container(
                        content=ft.Text(
                            "Select or drag a jewelry photograph to begin.\n"
                            "Click '✨ Try Demo Ring' to instantly load a sample solitaire.",
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

        # Single Full Image Display Box (Fully displays selected image or result)
        self.main_img = ft.Image(src="", fit=ft.BoxFit.CONTAIN, border_radius=12)
        self.display_box = ft.Container(
            content=self.main_img,
            bgcolor=StudioColors.CANVAS_BG,
            border=ft.Border.all(1.5, StudioColors.CARD_BORDER),
            border_radius=14,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=14, color="#00000020", offset=ft.Offset(0, 4)),
            alignment=ft.Alignment(0, 0),
            expand=True,
            padding=16,
            visible=False,
        )

        # Loading Overlay
        self.loading_step = ft.Text("Processing AI Workflow...", size=14, weight=ft.FontWeight.W_800, color=StudioColors.TEXT_PRIMARY)
        self.loading_sub = ft.Text("Executing engine...", size=11, color=StudioColors.TEXT_MUTED)
        self.loading_overlay = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    ft.ProgressRing(color=StudioColors.GOLD_PRIMARY, stroke_width=4, width=56, height=56),
                    self.loading_step,
                    self.loading_sub,
                ],
            ),
            alignment=ft.Alignment(0, 0),
            expand=True,
            visible=False,
        )

        self.view_stack = ft.Stack(
            controls=[
                self.empty_state,
                self.display_box,
                self.loading_overlay,
            ],
            expand=True,
        )

        self.content = ft.Column(
            spacing=14,
            controls=[
                toolbar,
                self.view_stack,
            ],
            expand=True,
        )

    def update_from_state(self, state: StudioState) -> None:
        self.btn_download.disabled = state.output_path is None or state.is_processing

        # 1. Processing state
        if state.is_processing:
            self.loading_overlay.visible = True
            self.empty_state.visible = False
            self.display_box.visible = False
            self.loading_step.value = state.status_step
            self.loading_sub.value = state.status_subtext
            self.canvas_badge.content.value = "PROCESSING..."
            self.canvas_badge.content.color = StudioColors.GOLD_PRIMARY
            return

        self.loading_overlay.visible = False

        # 2. Empty state (No image loaded)
        if not state.input_data_uri and not state.output_data_uri:
            self.empty_state.visible = True
            self.display_box.visible = False
            self.canvas_title.value = "IMAGE INSPECTION CANVAS"
            self.canvas_title.color = StudioColors.TEXT_PRIMARY
            self.canvas_badge.content.value = "IDLE"
            self.canvas_badge.content.color = StudioColors.TEXT_MUTED
            self.canvas_badge.border = ft.Border.all(1, StudioColors.CARD_BORDER)
            return

        # 3. Image Present -> Show selected or processed image FULLY!
        self.empty_state.visible = False
        self.display_box.visible = True

        is_bg_remover = (state.active_mode == EnhancementMode.REMOVE_BG)

        if state.output_data_uri:
            # Processed result is available: display output image fully
            self.main_img.src = state.output_data_uri
            if is_bg_remover:
                self.canvas_title.value = "ALPHA CUTOUT (100% ORIGINAL PIXELS)"
                self.canvas_title.color = "#34D399"
                self.canvas_badge.content.value = "TRANSPARENT PNG"
                self.canvas_badge.content.color = "#10B981"
                self.canvas_badge.border = ft.Border.all(1, "#059669")
                self.display_box.border = ft.Border.all(1.5, "#059669")
                self.display_box.image = ft.DecorationImage(src="assets/checkerboard.png", repeat=ft.ImageRepeat.REPEAT)
            else:
                self.canvas_title.value = "4X SUPER-RESOLUTION RESULT"
                self.canvas_title.color = "#60A5FA"
                self.canvas_badge.content.value = "4X VULKAN MASTER"
                self.canvas_badge.content.color = "#3B82F6"
                self.canvas_badge.border = ft.Border.all(1, "#3B82F6")
                self.display_box.border = ft.Border.all(1.5, "#3B82F6")
                self.display_box.image = None
        else:
            # User selected an image: display ONLY that selected image fully
            self.main_img.src = state.input_data_uri
            self.canvas_title.value = "SELECTED IMAGE (ORIGINAL)"
            self.canvas_title.color = StudioColors.TEXT_PRIMARY
            w = state.metrics.original_width
            h = state.metrics.original_height
            self.canvas_badge.content.value = f"{w} × {h} PX"
            self.canvas_badge.content.color = StudioColors.TEXT_SECONDARY
            self.canvas_badge.border = ft.Border.all(1, StudioColors.CARD_BORDER)
            self.display_box.border = ft.Border.all(1.5, StudioColors.CARD_BORDER)
            self.display_box.image = None
