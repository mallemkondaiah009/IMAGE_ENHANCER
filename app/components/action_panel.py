"""
app/components/action_panel.py
Primary CTA, progress bar, and status readout panel with animated action button.
"""
from typing import Callable
import flet as ft
from app.models import StudioState, ProcessingStatus, EnhancementMode, CutoutBackground
from app.theme import StudioColors, StudioStyles
from .animated_button import AnimatedButton


class ActionPanel(ft.Container):
    def __init__(self, on_process_click: Callable[[], None]):
        super().__init__()
        self._on_process_click = on_process_click
        self._current_mode = EnhancementMode.ENHANCE

        self.process_btn = AnimatedButton(
            text="ENHANCE PHOTO (4X SUPER-RES)",
            icon=ft.Icons.AUTO_AWESOME,
            gradient_colors=["#2563EB", "#1D4ED8"],
            hover_gradient_colors=["#3B82F6", "#2563EB"],
            glow_color="#2563EB66",
            height=46,
            font_size=12,
            border_radius=4,
            disabled=True,
            on_click=lambda e: self._on_process_click(),
        )

        self.progress_bar = ft.ProgressBar(
            value=0,
            color="#2563EB",
            bgcolor="#1E293B",
            visible=False,
        )

        self.status_icon = ft.Icon(ft.Icons.INFO_OUTLINED, color=StudioColors.TEXT_MUTED, size=14)
        self.status_log = ft.Text(
            "Ready — Load a jewelry photo to begin.",
            size=11,
            color=StudioColors.TEXT_MUTED,
            expand=True,
        )

        self.status_card = ft.Container(
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    self.status_icon,
                    self.status_log,
                ],
            ),
            bgcolor="#05070D",
            border=ft.Border.all(1, "#1E293B"),
            border_radius=4,
            padding=ft.Padding.symmetric(vertical=8, horizontal=10),
        )

        self.content = ft.Column(
            spacing=10,
            controls=[
                self.process_btn,
                self.progress_bar,
                self.status_card,
            ],
        )

    def update_from_state(self, state: StudioState) -> None:
        # Dynamic theme sync based on active pipeline mode
        if state.active_mode == EnhancementMode.ENHANCE:
            self._current_mode = state.active_mode
            self.process_btn.update_appearance(
                text="ENHANCE PHOTO (4X SUPER-RES)",
                icon=ft.Icons.AUTO_AWESOME,
                gradient_colors=["#2563EB", "#1D4ED8"],
                hover_gradient_colors=["#3B82F6", "#2563EB"],
                glow_color="#2563EB66",
            )
            self.progress_bar.color = "#2563EB"
        elif state.active_mode == EnhancementMode.REMOVE_BG:
            self._current_mode = state.active_mode
            if state.is_batch and state.batch_total > 0:
                btn_text = f"REMOVE BG FOR ALL {state.batch_total} IMAGES"
            elif getattr(state, "cutout_bg", None) == CutoutBackground.WHITE:
                btn_text = "REMOVE BACKGROUND (BG WHITE)"
            elif getattr(state, "cutout_bg", None) == CutoutBackground.BLACK:
                btn_text = "REMOVE BACKGROUND (BG BLACK)"
            else:
                btn_text = "REMOVE BACKGROUND (TRANSPARENT)"

            self.process_btn.update_appearance(
                text=btn_text,
                icon=ft.Icons.AUTO_AWESOME_MOTION if state.is_batch else ft.Icons.CONTENT_CUT,
                gradient_colors=["#059669", "#047857"],
                hover_gradient_colors=["#10B981", "#059669"],
                glow_color="#05966966",
            )
            self.progress_bar.color = "#059669"

        self.process_btn.disabled = state.is_processing or (state.input_image is None)
        self.progress_bar.visible = state.is_processing
        self.progress_bar.value = None if state.is_processing else 0

        self.status_log.value = state.status_message
        if state.status == ProcessingStatus.ERROR:
            self.status_log.color = StudioColors.ERROR_RED
            self.status_icon.name = ft.Icons.ERROR_OUTLINE
            self.status_icon.color = StudioColors.ERROR_RED
        elif state.status == ProcessingStatus.COMPLETED:
            self.status_log.color = StudioColors.SUCCESS_TEXT
            self.status_icon.name = ft.Icons.CHECK_CIRCLE_OUTLINE
            self.status_icon.color = StudioColors.SUCCESS_GREEN
        elif state.is_processing:
            color = "#2563EB" if state.active_mode == EnhancementMode.ENHANCE else "#059669"
            self.status_log.color = color
            self.status_icon.name = ft.Icons.SYNC
            self.status_icon.color = color
            self.status_card.border = ft.Border.all(1, f"{color}88")
            self.status_card.bgcolor = f"{color}15"
        else:
            self.status_card.border = ft.Border.all(1, "#1E293B")
            self.status_card.bgcolor = "#05070D"
            self.status_log.color = StudioColors.TEXT_MUTED
            self.status_icon.name = ft.Icons.INFO_OUTLINED
            self.status_icon.color = StudioColors.TEXT_MUTED
