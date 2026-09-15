"""
app/components/pipeline_selector.py
Mode selector widget for 4x Polish / Background Cutout / Dual Combo.
"""
from typing import Callable
import flet as ft
from app.models import EnhancementMode, StudioState
from app.theme import StudioColors


class PipelineSelector(ft.Container):
    def __init__(self, on_mode_change: Callable[[EnhancementMode], None]):
        super().__init__()
        self._on_mode_change = on_mode_change

        self.radio_group = ft.RadioGroup(
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Radio(
                        value=EnhancementMode.ENHANCE.value,
                        label="✦ Pure Natural AI Polish (4x Super-Res + Clarity)",
                        fill_color=StudioColors.GOLD_PRIMARY,
                    ),
                    ft.Radio(
                        value=EnhancementMode.REMOVE_BG.value,
                        label="✂ AI Studio Background Cutout (BiRefNet Cutout)",
                        fill_color=StudioColors.GOLD_PRIMARY,
                    ),
                    ft.Radio(
                        value=EnhancementMode.COMBO.value,
                        label="⚡ Complete Dual Studio (4x Polish + Cutout)",
                        fill_color=StudioColors.GOLD_PRIMARY,
                    ),
                ],
            ),
            value=EnhancementMode.ENHANCE.value,
            on_change=self._handle_change,
        )

        self.content = ft.Column(
            spacing=8,
            controls=[
                ft.Text("Enhancement Pipeline", size=13, weight=ft.FontWeight.W_700, color=StudioColors.GOLD_MUTED),
                self.radio_group,
            ],
        )

    def _handle_change(self, e):
        mode = EnhancementMode(self.radio_group.value)
        self._on_mode_change(mode)

    def update_from_state(self, state: StudioState) -> None:
        if self.radio_group.value != state.active_mode.value:
            self.radio_group.value = state.active_mode.value
