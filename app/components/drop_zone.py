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
        on_sample_click: Callable[[], None] = None,
        on_folder_click: Callable[[], None] = None,
    ):
        super().__init__()
        self.bgcolor = StudioColors.CARD_BG
        self.border = ft.Border.all(1.5, StudioColors.CARD_BORDER)
        self.border_radius = StudioStyles.RADIUS_CARD
        self.padding = 16

        self.thumbnail_img = ft.Image(
            src="",
            width=52,
            height=52,
            fit=ft.BoxFit.COVER,
            border_radius=2,
            visible=False,
        )

        self.file_info_title = ft.Text(
            "No image loaded",
            size=12,
            weight=ft.FontWeight.W_800,
            color=StudioColors.TEXT_PRIMARY,
            no_wrap=True,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.file_info_sub = ft.Text(
            "Select or drop a photo to begin",
            size=11,
            color=StudioColors.TEXT_MUTED,
            no_wrap=True,
            overflow=ft.TextOverflow.ELLIPSIS,
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
            bgcolor="#0B0F19",
            border=ft.Border.all(1, "#1E293B"),
            border_radius=4,
            padding=10,
            visible=False,
        )

        self.zone_title = ft.Text(
            "Load Jewelry Photograph",
            size=13,
            weight=ft.FontWeight.W_800,
            color=StudioColors.TEXT_PRIMARY,
        )

        self.zone_sub = ft.Text(
            "Solitaire rings, diamonds, gems, gold (PNG, JPG, WebP)",
            size=11,
            color=StudioColors.TEXT_MUTED,
        )

        self.browse_btn = ft.OutlinedButton(
            "Browse File",
            icon=ft.Icons.IMAGE_OUTLINED,
            expand=True,
            height=40,
            style=ft.ButtonStyle(
                color={ft.ControlState.HOVERED: "#FFFFFF", "": "#CBD5E1"},
                bgcolor={ft.ControlState.HOVERED: "#1E293B", "": "#111827"},
                side={ft.ControlState.HOVERED: ft.BorderSide(1.5, "#3B82F6"), "": ft.BorderSide(1, "#1E293B")},
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=ft.Padding.symmetric(vertical=8, horizontal=12),
                animation_duration=180,
            ),
            on_click=lambda e: on_browse_click(),
        )

        self.folder_btn = ft.OutlinedButton(
            "Select Folder",
            icon=ft.Icons.DRIVE_FOLDER_UPLOAD,
            expand=True,
            height=40,
            visible=True,
            style=ft.ButtonStyle(
                color={ft.ControlState.HOVERED: "#FFFFFF", "": "#34D399"},
                bgcolor={ft.ControlState.HOVERED: "#059669", "": "#064E3B40"},
                side={ft.ControlState.HOVERED: ft.BorderSide(1.5, "#10B981"), "": ft.BorderSide(1, "#059669")},
                shape=ft.RoundedRectangleBorder(radius=4),
                padding=ft.Padding.symmetric(vertical=8, horizontal=12),
                animation_duration=180,
            ),
            on_click=lambda e: on_folder_click() if on_folder_click else None,
        )

        self.content = ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED, color=StudioColors.GOLD_PRIMARY, size=20),
                            width=38,
                            height=38,
                            bgcolor=StudioColors.GOLD_CHIP_BG,
                            border=ft.Border.all(1, StudioColors.GOLD_CHIP_BORDER),
                            border_radius=4,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            spacing=1,
                            controls=[
                                self.zone_title,
                                self.zone_sub,
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[self.browse_btn, self.folder_btn],
                ),
                self.loaded_badge,
            ],
        )

    def update_from_state(self, state: StudioState) -> None:
        from app.models import EnhancementMode
        self.zone_title.value = "Load Image or Folder"
        self.zone_sub.value = "Select single photo or an entire image folder (PNG, JPG, WebP)"
        self.folder_btn.visible = True

        if state.is_batch and state.batch_folder_name:
            self.thumbnail_img.src = state.input_data_uri or ""
            self.thumbnail_img.visible = bool(state.input_data_uri)
            self.file_info_title.value = f"📁 {state.batch_folder_name}"
            action_desc = "batch 4x enhancement" if state.active_mode == EnhancementMode.ENHANCE else "batch BG removal"
            self.file_info_sub.value = f"{state.batch_total} images found · Ready for {action_desc}"
            self.loaded_badge.visible = True
        elif state.input_data_uri and state.input_path:
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
