"""
app/components/action_panel.py
Primary CTA, progress bar, and status readout panel with animated action button.
"""
from typing import Callable
import flet as ft
from app.models import StudioState, ProcessingStatus, EnhancementMode
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
            height=48,
            font_size=13,
            border_radius=24,
            disabled=True,
            on_click=lambda e: self._on_process_click(),
        )

        self.progress_bar = ft.ProgressBar(
            value=0,
            color="#2563EB",
            bgcolor="#E2E8F0",
            visible=False,
        )

        self.status_log = ft.Text(
            "Ready — Load a jewelry photo to begin.",
            size=11,
            color=StudioColors.TEXT_MUTED,
        )

        self.content = ft.Column(
            spacing=10,
            controls=[
                self.process_btn,
                self.progress_bar,
                ft.Container(
                    content=self.status_log,
                    padding=ft.Padding.symmetric(horizontal=4),
                ),
            ],
        )

    def update_from_state(self, state: StudioState) -> None:
        # Dynamic theme sync based on active pipeline mode
        if state.active_mode != self._current_mode:
            self._current_mode = state.active_mode
            if state.active_mode == EnhancementMode.ENHANCE:
                self.process_btn.update_appearance(
                    text="ENHANCE PHOTO (4X SUPER-RES)",
                    icon=ft.Icons.AUTO_AWESOME,
                    gradient_colors=["#2563EB", "#1D4ED8"],
                    hover_gradient_colors=["#3B82F6", "#2563EB"],
                    glow_color="#2563EB66",
                )
                self.progress_bar.color = "#2563EB"
            elif state.active_mode == EnhancementMode.REMOVE_BG:
                self.process_btn.update_appearance(
                    text="REMOVE BACKGROUND (AI CUTOUT)",
                    icon=ft.Icons.CONTENT_CUT,
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
        elif state.status == ProcessingStatus.COMPLETED:
            self.status_log.color = StudioColors.SUCCESS_TEXT
        elif state.is_processing:
            self.status_log.color = "#2563EB" if state.active_mode == EnhancementMode.ENHANCE else "#059669"
        else:
            self.status_log.color = StudioColors.TEXT_MUTED
