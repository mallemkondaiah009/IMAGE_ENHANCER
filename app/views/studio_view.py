"""
app/views/studio_view.py
Main Studio Screen View — Pure luxury desktop workspace with zero page reloads.
Unified single-page layout with centered dual-mode switcher in the header,
clean minimal controls (DropZone & ActionPanel), and high-performance Vulkan & BiRefNet engines.
"""
import os
import shutil
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
        self._dialog_lock = False
        pictures_dir = os.path.expanduser("~/Pictures")
        self._last_browse_dir = pictures_dir if os.path.exists(pictures_dir) else os.path.expanduser("~/Desktop")

        # ── 1. Create Child Components ────────────────────────────────────────
        self.header = HeaderBar(on_mode_change=self._handle_mode_change)

        self.drop_zone = DropZone(
            on_browse_click=self._handle_browse,
            on_folder_click=self._handle_folder_pick,
        )

        self.action_panel = ActionPanel(
            on_process_click=self._handle_process,
        )

        self.comparison_canvas = ComparisonCanvas(
            on_save_click=self._handle_save,
            on_cutout_bg_change=self._handle_cutout_bg_change,
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
            shadow=None,
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
            if self.app_page:
                self.app_page.update()
        except Exception:
            pass

    # ── Event Callbacks (Single-Instance Instant Dialogs) ─────────────────────
    async def _async_load_image(self, file_path: str) -> None:
        self.vm.load_image(file_path)

    async def _async_load_folder(self, folder_path: str) -> None:
        self.vm.load_folder(folder_path)

    def _handle_browse(self) -> None:
        if getattr(self, "_dialog_lock", False):
            return
        self._dialog_lock = True
        initial_dir = self._last_browse_dir if (self._last_browse_dir and os.path.exists(self._last_browse_dir)) else os.path.expanduser("~")

        def _worker():
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                root.update()
                chosen = filedialog.askopenfilename(
                    title="Select Jewelry Image",
                    initialdir=initial_dir,
                    filetypes=[
                        ("Supported Images", "*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.tiff"),
                        ("JPEG Image (*.jpg, *.jpeg)", "*.jpg;*.jpeg"),
                        ("PNG Image (*.png)", "*.png"),
                        ("WebP Image (*.webp)", "*.webp"),
                        ("All Files (*.*)", "*.*"),
                    ],
                )
                root.destroy()
                if chosen:
                    self._last_browse_dir = os.path.dirname(chosen)
                    self.app_page.run_task(self._async_load_image, chosen)
            except Exception as exc:
                print(f"[-] Browse error: {exc}")
            finally:
                self._dialog_lock = False

        import threading
        threading.Thread(target=_worker, daemon=True).start()

    def _handle_folder_pick(self) -> None:
        if getattr(self, "_dialog_lock", False):
            return
        self._dialog_lock = True
        initial_dir = self._last_browse_dir if (self._last_browse_dir and os.path.exists(self._last_browse_dir)) else os.path.expanduser("~")

        def _worker():
            try:
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                root.update()
                mode_title = "Batch 4x Super-Resolution" if self.vm.state.active_mode == EnhancementMode.ENHANCE else "Batch Background Removal"
                chosen = filedialog.askdirectory(
                    title=f"Select Image Folder for {mode_title}",
                    initialdir=initial_dir,
                )
                root.destroy()
                if chosen:
                    self._last_browse_dir = chosen
                    self.app_page.run_task(self._async_load_folder, chosen)
            except Exception as exc:
                print(f"[-] Folder pick error: {exc}")
            finally:
                self._dialog_lock = False

        import threading
        threading.Thread(target=_worker, daemon=True).start()

    def _handle_sample(self) -> None:
        self.vm.load_sample_image()

    def _handle_mode_change(self, mode: EnhancementMode) -> None:
        self.vm.set_enhancement_mode(mode)

    def _handle_cutout_bg_change(self, bg) -> None:
        self.vm.set_cutout_bg(bg)

    def _handle_process(self) -> None:
        self.app_page.run_task(self.vm.process_image)

    def _handle_save(self) -> None:
        if getattr(self, "_dialog_lock", False):
            return
        self._dialog_lock = True

        state = self.vm.state
        initial_dir = self._last_browse_dir if (self._last_browse_dir and os.path.exists(self._last_browse_dir)) else os.path.expanduser("~")

        def _worker():
            try:
                import tkinter as tk
                from tkinter import filedialog

                if state.is_batch:
                    if not state.batch_output_dir or not os.path.exists(state.batch_output_dir):
                        return
                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    root.update()
                    folder_name = state.batch_folder_name or "batch_output"
                    dest_dir = filedialog.askdirectory(
                        title=f"Select Destination to Download Folder '{folder_name}'",
                        initialdir=initial_dir,
                    )
                    root.destroy()
                    if dest_dir:
                        self._last_browse_dir = dest_dir
                        self.vm.export_folder(dest_dir)
                else:
                    if not state.output_path or not os.path.exists(state.output_path):
                        return
                    orig_name = os.path.basename(state.input_path) if state.input_path else "image"
                    orig_stem, _ = os.path.splitext(orig_name)
                    ext = os.path.splitext(state.output_path)[1].lstrip(".").lower() or "jpg"
                    filetypes = [("PNG Image", "*.png"), ("All files", "*.*")] if ext == "png" else [("JPEG Image", "*.jpg;*.jpeg"), ("All files", "*.*")]

                    # In Image Enhance: add '-enhanced' to uploaded filename
                    # In BG Removal: use same filename as uploaded image
                    if state.active_mode == EnhancementMode.ENHANCE:
                        base_name = f"{orig_stem}-enhanced"
                    elif state.active_mode == EnhancementMode.REMOVE_BG:
                        base_name = f"{orig_stem}"
                    else:
                        base_name = f"{orig_stem}-enhanced"

                    # Prevent duplicate file name if file already exists in initial_dir
                    candidate_file = f"{base_name}.{ext}"
                    if os.path.exists(os.path.join(initial_dir, candidate_file)):
                        counter = 1
                        candidate_file = f"{base_name}_{counter}.{ext}"
                        while os.path.exists(os.path.join(initial_dir, candidate_file)):
                            counter += 1
                            candidate_file = f"{base_name}_{counter}.{ext}"

                    initial_file = candidate_file

                    root = tk.Tk()
                    root.withdraw()
                    root.attributes("-topmost", True)
                    root.update()
                    dest = filedialog.asksaveasfilename(
                        title="Download Processed Jewelry Image",
                        initialdir=initial_dir,
                        initialfile=initial_file,
                        defaultextension=f".{ext}",
                        filetypes=filetypes,
                    )
                    root.destroy()
                    if dest:
                        self._last_browse_dir = os.path.dirname(dest)
                        self.vm.export_image(dest)
            except Exception as exc:
                print(f"[-] Save error: {exc}")
            finally:
                self._dialog_lock = False

        import threading
        threading.Thread(target=_worker, daemon=True).start()
