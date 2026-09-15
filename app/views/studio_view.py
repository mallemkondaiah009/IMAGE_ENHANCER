"""
app/views/studio_view.py
Main Studio Screen View — Pure luxury desktop workspace with zero page reloads.
Unified single-page layout with centered dual-mode switcher in the header,
clean minimal controls (DropZone & ActionPanel), and high-performance Vulkan & BiRefNet engines.
"""
import os
import uuid
import flet as ft
from app.viewmodels import StudioViewModel
from app.models import EnhancementMode
from app.theme import StudioColors, StudioStyles
from app.components import (
    HeaderBar,
    DropZone,
    ActionPanel,
    ComparisonCanvas,
    MetricsBar,
)


class StudioView(ft.Container):
    def __init__(self, page: ft.Page, viewmodel: StudioViewModel):
        super().__init__()
        self.app_page = page
        self.vm = viewmodel
        self.expand = True
        self.bgcolor = StudioColors.BG_WHITE

        # Attach file pickers
        self.file_picker = ft.FilePicker()
        self.save_file_picker = ft.FilePicker()
        if hasattr(self.app_page, "services"):
            self.app_page.services.extend([self.file_picker, self.save_file_picker])

        # ── 1. Create Child Components ────────────────────────────────────────
        self.header = HeaderBar(on_mode_change=self._handle_mode_change)

        self.drop_zone = DropZone(
            on_browse_click=self._handle_browse,
            on_sample_click=self._handle_sample,
        )

        self.action_panel = ActionPanel(
            on_process_click=self._handle_process,
        )

        self.comparison_canvas = ComparisonCanvas(
            on_save_click=self._handle_save,
        )

        self.metrics_bar = MetricsBar()

        # ── 2. Clean Left Control Panel (DropZone & ActionPanel Only) ────────
        control_panel = ft.Container(
            width=390,
            content=ft.Column(
                spacing=16,
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[
                    self.drop_zone,
                    self.action_panel,
                ],
            ),
            bgcolor=StudioColors.CARD_BG,
            border=ft.Border.all(1.5, StudioColors.CARD_BORDER),
            border_radius=StudioStyles.RADIUS_CARD,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=16, color="#00000008", offset=ft.Offset(0, 4)),
            padding=16,
        )

        # ── 3. Right Workspace Panel ──────────────────────────────────────────
        workspace_wrapper = ft.Container(
            content=ft.Column(
                spacing=12,
                controls=[
                    self.comparison_canvas,
                    self.metrics_bar,
                ],
                expand=True,
            ),
            expand=True,
        )

        # ── 4. Main Two-Panel Layout ──────────────────────────────────────────
        main_layout = ft.Row(
            expand=True,
            spacing=14,
            controls=[
                control_panel,
                workspace_wrapper,
            ],
        )

        self.content = ft.Column(
            spacing=12,
            expand=True,
            controls=[
                self.header,
                main_layout,
            ],
        )

        # ── 5. Subscribe to ViewModel updates ─────────────────────────────────
        self.vm.add_listener(self._render_state)
        # Initial state sync
        self._render_state()

    def _render_state(self) -> None:
        """Reactive observer callback called whenever ViewModel state updates."""
        state = self.vm.state
        self.header.set_active_mode(state.active_mode)
        self.drop_zone.update_from_state(state)
        self.action_panel.update_from_state(state)
        self.comparison_canvas.update_from_state(state)
        self.metrics_bar.update_from_state(state)
        try:
            if self.page:
                self.page.update()
        except Exception:
            pass

    # ── Event Callbacks ───────────────────────────────────────────────────────
    def _handle_browse(self) -> None:
        async def _pick():
            try:
                files = await self.file_picker.pick_files(
                    dialog_title="Select Jewelry Image",
                    file_type=ft.FilePickerFileType.IMAGE,
                )
                if files and len(files) > 0:
                    self.vm.load_image(files[0].path)
                    return
            except Exception:
                pass

            # Tkinter fallback
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                chosen = filedialog.askopenfilename(
                    title="Select Jewelry Image",
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

    def _handle_mode_change(self, mode: EnhancementMode) -> None:
        self.vm.set_enhancement_mode(mode)

    def _handle_process(self) -> None:
        self.app_page.run_task(self.vm.process_image)

    def _handle_save(self) -> None:
        state = self.vm.state
        if not state.output_path or not os.path.exists(state.output_path):
            return

        ext = os.path.splitext(state.output_path)[1].lstrip(".").lower() or "jpg"
        allowed = ["png"] if ext == "png" else ["jpg", "jpeg"]
        filetypes = [("PNG Image", "*.png"), ("All files", "*.*")] if ext == "png" else [("JPEG Image", "*.jpg;*.jpeg"), ("All files", "*.*")]

        async def _save():
            try:
                dest = await self.save_file_picker.save_file(
                    dialog_title="Download Processed Jewelry Image",
                    file_name=f"lumiere_{state.active_mode.value}_{uuid.uuid4().hex[:6]}.{ext}",
                    allowed_extensions=allowed,
                )
                if dest:
                    self.vm.export_image(dest)
                    return
            except Exception:
                pass

            # Tkinter fallback
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                dest = filedialog.asksaveasfilename(
                    title="Download Processed Jewelry Image",
                    defaultextension=f".{ext}",
                    filetypes=filetypes,
                )
                root.destroy()
                if dest:
                    self.vm.export_image(dest)
            except Exception as inner:
                print(f"[-] Save error: {inner}")

        self.app_page.run_task(_save)
