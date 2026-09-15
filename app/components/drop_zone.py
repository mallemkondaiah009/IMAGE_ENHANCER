"""
app/components/drop_zone.py
Image input drop zone with file picker and thumbnail preview in pure white styling.
"""
from typing import Callable
import os
import flet as ft
from app.models import StudioState
from app.theme import StudioColors, StudioStyles


class DropZone(ft.Container):
    def __init__(
        self,
        on_browse_click: Callable[[], None],
        on_sample_click: Callable[[], None],
    ):
        super().__init__()
        self.bgcolor = StudioColors.CARD_BG
        self.border = ft.Border.all(1.5, StudioColors.CARD_BORDER)
        self.border_radius = StudioStyles.RADIUS_CARD
        self.padding = 16

        self.thumbnail_img = ft.Image(
            src="",
            width=54,
            height=54,
            fit=ft.BoxFit.COVER,
            border_radius=8,
            visible=False,
        )

        self.file_info_title = ft.Text(
            "No image loaded",
            size=12,
            weight=ft.FontWeight.W_700,
            color=StudioColors.TEXT_PRIMARY,
        )

        self.file_info_sub = ft.Text(
            "Select or drop a photo to begin",
            size=10,
            color=StudioColors.TEXT_MUTED,
        )

        self.loaded_badge = ft.Container(
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.thumbnail_img,
                    ft.Column(
                        spacing=2,
                        expand=True,
                        controls=[self.file_info_title, self.file_info_sub],
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CHECK_CIRCLE, color=StudioColors.SUCCESS_GREEN, size=18),
                        padding=4,
                    ),
                ],
            ),
            bgcolor=StudioColors.SURFACE_MUTED,
            border=ft.Border.all(1, StudioColors.CARD_BORDER),
            border_radius=10,
            padding=10,
            visible=False,
        )

        browse_btn = ft.OutlinedButton(
            "Browse File",
            icon=ft.Icons.FOLDER_OPEN,
            expand=True,
            style=ft.ButtonStyle(
                color={ft.ControlState.HOVERED: "#FFFFFF", "": StudioColors.TEXT_SECONDARY},
                bgcolor={ft.ControlState.HOVERED: "#1E293B", "": ft.Colors.TRANSPARENT},
                side={ft.ControlState.HOVERED: ft.BorderSide(1.5, StudioColors.GOLD_PRIMARY), "": ft.BorderSide(1, StudioColors.CARD_BORDER)},
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.Padding.symmetric(vertical=10, horizontal=14),
                animation_duration=180,
            ),
            on_click=lambda e: on_browse_click(),
        )

        sample_btn = ft.FilledButton(
            "✨ Try Demo Ring",
            expand=True,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.HOVERED: "#FFFFFF",
                    "": "#60A5FA",
                },
                bgcolor={
                    ft.ControlState.HOVERED: "#1E293B",
                    "": StudioColors.GOLD_CHIP_BG,
                },
                side={
                    ft.ControlState.HOVERED: ft.BorderSide(1.5, StudioColors.GOLD_PRIMARY),
                    "": ft.BorderSide(1, StudioColors.GOLD_CHIP_BORDER),
                },
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.Padding.symmetric(vertical=10, horizontal=14),
                animation_duration=180,
            ),
            on_click=lambda e: on_sample_click(),
        )

        self.content = ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED, color=StudioColors.GOLD_PRIMARY, size=22),
                            width=42,
                            height=42,
                            bgcolor=StudioColors.GOLD_CHIP_BG,
                            border=ft.Border.all(1, StudioColors.GOLD_CHIP_BORDER),
                            border_radius=21,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            spacing=1,
                            controls=[
                                ft.Text(
                                    "Load Jewelry Photograph",
                                    size=13,
                                    weight=ft.FontWeight.W_800,
                                    color=StudioColors.TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    "Solitaire rings, diamonds, gems, gold (PNG, JPG, WebP)",
                                    size=11,
                                    color=StudioColors.TEXT_MUTED,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[browse_btn, sample_btn],
                ),
                self.loaded_badge,
            ],
        )

    def update_from_state(self, state: StudioState) -> None:
        if state.input_data_uri and state.input_path:
            filename = os.path.basename(state.input_path)
            w = state.metrics.original_width
            h = state.metrics.original_height
            kb = state.metrics.original_kb
            self.thumbnail_img.src = state.input_data_uri
            self.thumbnail_img.visible = True
            self.file_info_title.value = filename
            self.file_info_sub.value = f"{w} × {h} px · {kb} KB · Loaded"
            self.loaded_badge.visible = True
        else:
            self.thumbnail_img.visible = False
            self.loaded_badge.visible = False
