"""
app/views/remove_bg_view.py
Dedicated AI Background Removal & Transparent Cutout Studio Screen in pure white luxury styling.
"""
import os
import uuid
from typing import Callable
import flet as ft
from app.viewmodels import StudioViewModel
from app.models import EnhancementMode, ViewMode
from app.theme import StudioColors, StudioStyles
from app.components import (
    DropZone,
    SpecsCard,
    ComparisonCanvas,
    MetricsBar,
    AnimatedButton,
)


class RemoveBgView(ft.Container):
    def __init__(self, page: ft.Page, viewmodel: StudioViewModel, on_back_click: Callable[[], None]):
        super().__init__()
        self.app_page = page
        self.vm = viewmodel
        self._on_back_click = on_back_click
        self.expand = True
        self.bgcolor = StudioColors.BG_WHITE

        # File Pickers
        self.file_picker = ft.FilePicker()
        self.save_file_picker = ft.FilePicker()
        if hasattr(self.app_page, "services"):
            self.app_page.services.extend([self.file_picker, self.save_file_picker])

        # ── 1. Top Navigation Bar ─────────────────────────────────────────────
        btn_back = ft.OutlinedButton(
            "← Back to Dashboard",
            icon=ft.Icons.ARROW_BACK,
            style=StudioStyles.ghost_button(),
            on_click=lambda e: self._on_back_click(),
        )

        title_badge = ft.Container(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.CONTENT_CUT, color=StudioColors.SUCCESS_GREEN, size=16),
                    ft.Text("AI Jewelry Background Cutout Studio", size=13, weight=ft.FontWeight.W_800, color=StudioColors.SUCCESS_TEXT),
                ],
            ),
            bgcolor=StudioColors.SUCCESS_BG,
            border=ft.Border.all(1, StudioColors.SUCCESS_BORDER),
            border_radius=18,
            padding=ft.Padding.symmetric(horizontal=14, vertical=6),
        )

        engine_status = ft.Container(
            content=ft.Row(
                spacing=7,
                controls=[
                    ft.Container(width=7, height=7, bgcolor=StudioColors.SUCCESS_GREEN, border_radius=4),
                    ft.Text("BIREFNET / U2NET READY", size=10, weight=ft.FontWeight.W_800, color=StudioColors.SUCCESS_TEXT),
                ],
            ),
            bgcolor=StudioColors.SUCCESS_BG,
            border=ft.Border.all(1, StudioColors.SUCCESS_BORDER),
            border_radius=18,
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
        )

        top_bar = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    btn_back,
                    ft.Row(spacing=10, controls=[title_badge, engine_status]),
                ],
            ),
            bgcolor=StudioColors.CARD_BG,
            border=ft.Border.all(1, StudioColors.CARD_BORDER),
            border_radius=StudioStyles.RADIUS_CARD,
            padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        )

        # ── 2. Left Control Panel ─────────────────────────────────────────────
        self.drop_zone = DropZone(
            on_browse_click=self._handle_browse,
            on_sample_click=self._handle_sample,
        )

        self.specs_card = SpecsCard()

        # Prominent Animated Cutout Button (Floating Pill)
        self.process_btn = AnimatedButton(
            text="REMOVE BACKGROUND (AI CUTOUT)",
            icon=ft.Icons.CONTENT_CUT,
            gradient_colors=["#059669", "#047857"],
            hover_gradient_colors=["#10B981", "#059669"],
            glow_color="#05966966",
            height=48,
            font_size=13,
            border_radius=24,
            disabled=True,
            on_click=lambda e: self._handle_process(),
        )

        self.progress_bar = ft.ProgressBar(
            value=0,
            color=StudioColors.SUCCESS_GREEN,
            bgcolor=StudioColors.CARD_BORDER,
            visible=False,
        )

        self.status_log = ft.Text(
            "Ready — Load a jewelry photo to extract transparent cutout.",
            size=11,
            color=StudioColors.TEXT_MUTED,
        )

        status_container = ft.Container(
            content=self.status_log,
            bgcolor=StudioColors.SURFACE_MUTED,
            border=ft.Border.all(1, StudioColors.CARD_BORDER),
            border_radius=10,
            padding=12,
        )

        left_panel = ft.Container(
            width=390,
            content=ft.Column(
                spacing=14,
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text("ALPHA CUTOUT CONTROLS", size=10, weight=ft.FontWeight.W_800, color=StudioColors.SUCCESS_TEXT),
                            ft.Text("BiRefNet AI Engine", size=18, weight=ft.FontWeight.W_800, color=StudioColors.TEXT_PRIMARY),
                            ft.Text("Segment solitaires, diamonds, gold and export transparent PNG", size=11, color=StudioColors.TEXT_MUTED),
                        ],
                    ),
                    self.drop_zone,
                    self.specs_card,
                    self.process_btn,
                    self.progress_bar,
                    status_container,
                ],
            ),
            bgcolor=StudioColors.CARD_BG,
            border=ft.Border.all(1.5, StudioColors.CARD_BORDER),
            border_radius=StudioStyles.RADIUS_CARD,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=16, color="#00000008", offset=ft.Offset(0, 4)),
            padding=18,
        )

        # ── 3. Right Workspace Panel ──────────────────────────────────────────
        self.comparison_canvas = ComparisonCanvas(
            on_view_change=self._handle_view_change,
            on_hold_toggle=self._handle_hold_toggle,
            on_save_click=self._handle_save,
        )

        self.metrics_bar = MetricsBar()

        workspace_wrapper = ft.Container(
            content=ft.Column(
                spacing=14,
                controls=[
                    self.comparison_canvas,
                    self.metrics_bar,
                ],
                expand=True,
            ),
            expand=True,
        )

        # ── 4. Main Layout ────────────────────────────────────────────────────
        studio_grid = ft.Row(
            expand=True,
            spacing=14,
            controls=[left_panel, workspace_wrapper],
        )

        self.content = ft.Column(
            spacing=12,
            expand=True,
            controls=[top_bar, studio_grid],
        )

    def update_from_state(self) -> None:
        state = self.vm.state
        self.drop_zone.update_from_state(state)
        self.comparison_canvas.update_from_state(state)
        self.metrics_bar.update_from_state(state)

        self.process_btn.disabled = state.is_processing or (state.input_image is None)
        self.progress_bar.visible = state.is_processing
        self.progress_bar.value = None if state.is_processing else 0
        self.status_log.value = state.status_message
        self.status_log.color = StudioColors.SUCCESS_TEXT if state.is_processing else StudioColors.TEXT_MUTED

    def _handle_browse(self) -> None:
        async def _pick():
            try:
                files = await self.file_picker.pick_files(
                    dialog_title="Select Jewelry Image for Cutout",
                    file_type=ft.FilePickerFileType.IMAGE,
                )
                if files and len(files) > 0:
                    self.vm.load_image(files[0].path)
                    return
            except Exception:
                pass

            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                chosen = filedialog.askopenfilename(
                    title="Select Jewelry Image for Cutout",
                    filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.webp"), ("All files", "*.*")],
                )
                root.destroy()
                if chosen:
                    self.vm.load_image(chosen)
            except Exception as inner:
                print(f"[-] Pick error: {inner}")

        self.app_page.run_task(_pick)

    def _handle_sample(self) -> None:
        self.vm.load_sample_image()

    def _handle_view_change(self, mode: ViewMode) -> None:
        self.vm.set_view_mode(mode)

    def _handle_hold_toggle(self) -> None:
        self.vm.toggle_hold_original()

    def _handle_process(self) -> None:
        self.vm.set_enhancement_mode(EnhancementMode.REMOVE_BG)
        self.app_page.run_task(self.vm.process_image)

    def _handle_save(self) -> None:
        state = self.vm.state
        if not state.output_path or not os.path.exists(state.output_path):
            return

        async def _save():
            try:
                dest = await self.save_file_picker.save_file(
                    dialog_title="Export Transparent Cutout",
                    file_name=f"lumiere_cutout_{uuid.uuid4().hex[:6]}.png",
                    allowed_extensions=["png"],
                )
                if dest:
                    self.vm.export_image(dest)
                    return
            except Exception:
                pass

            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                dest = filedialog.asksaveasfilename(
                    title="Export Transparent Cutout",
                    defaultextension=".png",
                    filetypes=[("PNG Image", "*.png"), ("All files", "*.*")],
                )
                root.destroy()
                if dest:
                    self.vm.export_image(dest)
            except Exception as inner:
                print(f"[-] Save error: {inner}")

        self.app_page.run_task(_save)
