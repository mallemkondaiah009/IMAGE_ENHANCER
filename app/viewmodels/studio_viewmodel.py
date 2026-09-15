"""
app/viewmodels/studio_viewmodel.py
Reactive ViewModel managing application state & dispatching background AI workers.
Follows Android ViewModel / Flutter ChangeNotifier pattern.
"""
import os
import time
import uuid
import base64
import asyncio
import shutil
from io import BytesIO
from typing import Callable, Optional
from PIL import Image

from app.config import settings
from app.models import (
    StudioState,
    EnhancementMode,
    ViewMode,
    ProcessingStatus,
    ImageMetrics,
)
from app.services.enhancement import run_natural_enhancement
from app.services.background import run_background_removal


def pil_to_data_uri(img: Image.Image, format_name: str = "PNG") -> str:
    buf = BytesIO()
    if img.mode == "RGBA":
        img.save(buf, format="PNG")
        mime = "image/png"
    else:
        img.convert("RGB").save(buf, format=format_name, quality=92)
        mime = "image/jpeg" if format_name.upper() == "JPEG" else "image/png"
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def file_to_data_uri(path: str) -> str:
    if not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = "image/webp" if ext == "webp" else ("image/png" if ext == "png" else "image/jpeg")
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


class StudioViewModel:
    def __init__(self):
        self.state = StudioState()
        self._listeners: list[Callable[[], None]] = []

    def add_listener(self, listener: Callable[[], None]) -> None:
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[], None]) -> None:
        if listener in self._listeners:
            self._listeners.remove(listener)

    def notify_listeners(self) -> None:
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                print(f"[-] Error notifying listener: {e}")

    def load_image(self, path: str) -> bool:
        """Loads an image into state and generates data URI."""
        try:
            if not os.path.exists(path):
                self.state.status = ProcessingStatus.ERROR
                self.state.status_message = f"File not found: {path}"
                self.notify_listeners()
                return False

            img = Image.open(path)
            orig_w, orig_h = img.size
            orig_kb = round(os.path.getsize(path) / 1024, 1)

            self.state.input_path = path
            self.state.input_image = img
            self.state.input_data_uri = pil_to_data_uri(img)

            # Reset previous results
            self.state.output_path = None
            self.state.output_image = None
            self.state.output_data_uri = None

            self.state.metrics = ImageMetrics(
                original_width=orig_w,
                original_height=orig_h,
                original_kb=orig_kb,
            )

            self.state.status = ProcessingStatus.IDLE
            self.state.status_message = f"Loaded {os.path.basename(path)} ({orig_w}×{orig_h} px). Ready to process."
            self.state.view_mode = ViewMode.SPLIT
            self.notify_listeners()
            return True
        except Exception as exc:
            self.state.status = ProcessingStatus.ERROR
            self.state.status_message = f"Failed to load image: {exc}"
            self.notify_listeners()
            return False

    def load_sample_image(self) -> bool:
        """Loads the bundled sample solitaire ring."""
        candidates = [
            os.path.join(settings.assets_dir, "sample_ring_small.jpg"),
            os.path.join(settings.assets_dir, "sample_ring_hd.jpg"),
            os.path.join(settings.engine_dir, "input.jpg"),
            os.path.join(settings.engine_dir, "input2.jpg"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return self.load_image(path)
        self.state.status = ProcessingStatus.ERROR
        self.state.status_message = "Sample image not found on disk."
        self.notify_listeners()
        return False

    def navigate_to(self, screen: str) -> None:
        """Navigates to 'home', 'enhance', or 'remove_bg'."""
        self.state.current_screen = screen
        if screen == "enhance":
            self.state.active_mode = EnhancementMode.ENHANCE
        elif screen == "remove_bg":
            self.state.active_mode = EnhancementMode.REMOVE_BG
        self.notify_listeners()

    def navigate_home(self) -> None:
        """Navigates back to the Home dashboard."""
        self.state.current_screen = "home"
        self.notify_listeners()

    def set_enhancement_mode(self, mode: EnhancementMode) -> None:
        if self.state.active_mode != mode:
            self.state.active_mode = mode
            self.state.output_path = None
            self.state.output_image = None
            self.state.output_data_uri = None
            if self.state.input_image:
                pipeline_name = "4x Super-Resolution" if mode == EnhancementMode.ENHANCE else "AI Background Cutout"
                self.state.status_message = f"Ready to run {pipeline_name} on {os.path.basename(self.state.input_path) if self.state.input_path else 'loaded image'}."
            self.notify_listeners()

    def set_view_mode(self, mode: ViewMode) -> None:
        self.state.view_mode = mode
        self.notify_listeners()

    def toggle_hold_original(self) -> None:
        """Toggles between original view and result view for comparison."""
        if self.state.view_mode == ViewMode.ORIGINAL:
            self.state.view_mode = ViewMode.ENHANCED if self.state.output_data_uri else ViewMode.SPLIT
        else:
            self.state.view_mode = ViewMode.ORIGINAL
        self.notify_listeners()

    def export_image(self, destination_path: str) -> bool:
        """Copies or converts the processed output image to the destination."""
        if not self.state.output_path or not os.path.exists(self.state.output_path):
            return False
        try:
            src_ext = os.path.splitext(self.state.output_path)[1].lower()
            dst_ext = os.path.splitext(destination_path)[1].lower()
            if src_ext == dst_ext or not dst_ext:
                shutil.copy2(self.state.output_path, destination_path)
            else:
                with Image.open(self.state.output_path) as im:
                    if dst_ext in (".jpg", ".jpeg"):
                        im.convert("RGB").save(destination_path, format="JPEG", quality=95, optimize=True)
                    elif dst_ext == ".png":
                        im.save(destination_path, format="PNG", optimize=True)
                    elif dst_ext == ".webp":
                        im.save(destination_path, format="WEBP", quality=90)
                    else:
                        shutil.copy2(self.state.output_path, destination_path)
            self.state.status_message = f"Exported successfully to {os.path.basename(destination_path)}"
            self.notify_listeners()
            return True
        except Exception as exc:
            self.state.status_message = f"Export failed: {exc}"
            self.notify_listeners()
            return False

    async def process_image(self) -> None:
        """Asynchronous execution pipeline running heavy models in worker threads."""
        if self.state.is_processing or not self.state.input_image or not self.state.input_path:
            return

        self.state.is_processing = True
        self.state.status = ProcessingStatus.PREPARING
        self.state.status_step = "Preparing high-res studio buffers..."
        self.state.status_subtext = f"Input resolution: {self.state.metrics.original_width}×{self.state.metrics.original_height} px"
        self.state.status_message = "[1/4] Preparing image buffers..."
        self.notify_listeners()
        await asyncio.sleep(0.05)

        req_id = uuid.uuid4().hex[:8]
        mode = self.state.active_mode
        start_time = time.time()

        output_ext = "png" if mode in (EnhancementMode.REMOVE_BG, EnhancementMode.COMBO) else "jpg"
        input_copy_path = os.path.join(settings.uploads_dir, f"input_{req_id}.png")
        ncnn_temp_path = os.path.join(settings.outputs_dir, f"ncnn_temp_{req_id}.png")
        final_out_path = os.path.join(settings.outputs_dir, f"lumiere_{mode.value}_{req_id}.{output_ext}")

        curr_img = self.state.input_image.copy()

        try:
            if mode == EnhancementMode.ENHANCE:
                self.state.status = ProcessingStatus.ENHANCING
                self.state.status_step = "Executing Real-ESRGAN Vulkan 4x Super-Resolution..."
                self.state.status_subtext = "Reconstructing diamond facets and gemstone crystal textures"
                self.state.status_message = "[2/4] Upscaling with Real-ESRGAN Vulkan..."
                self.notify_listeners()

                out_w, out_h = await asyncio.to_thread(
                    run_natural_enhancement,
                    curr_img,
                    input_copy_path,
                    ncnn_temp_path,
                    final_out_path,
                )

            elif mode == EnhancementMode.REMOVE_BG:
                self.state.status = ProcessingStatus.REMOVING_BG
                self.state.status_step = "Extracting Alpha Cutout..."
                self.state.status_subtext = "BiRefNet background removal (Zero Enhancement / Original Pixels Preserved)"
                self.state.status_message = "[2/3] Extracting pure background cutout..."
                self.notify_listeners()

                out_w, out_h, _ = await asyncio.to_thread(
                    run_background_removal,
                    curr_img,
                    final_out_path,
                )

            elif mode == EnhancementMode.COMBO:
                self.state.status = ProcessingStatus.ENHANCING
                self.state.status_step = "Phase 1: Real-ESRGAN Vulkan 4x Super-Resolution..."
                self.state.status_subtext = "Upscaling & polishing facets before background removal"
                self.state.status_message = "[2/4] Upscaling with Real-ESRGAN Vulkan..."
                self.notify_listeners()

                await asyncio.to_thread(
                    run_natural_enhancement,
                    curr_img,
                    input_copy_path,
                    ncnn_temp_path,
                    final_out_path,
                )

                self.state.status = ProcessingStatus.REMOVING_BG
                self.state.status_step = "Phase 2: Transparent Background Cutout..."
                self.state.status_subtext = "Isolating polished diamond solitaire from setting background"
                self.state.status_message = "[3/4] Background cutout on 4x enhanced image..."
                self.notify_listeners()

                enhanced_img = Image.open(final_out_path).convert("RGBA")
                out_w, out_h, _ = await asyncio.to_thread(
                    run_background_removal,
                    enhanced_img,
                    final_out_path,
                    (settings.target_output_width, settings.target_output_height),
                    settings.max_output_file_size_kb,
                )

            elapsed = round(time.time() - start_time, 2)
            out_bytes = os.path.getsize(final_out_path)
            file_kb = round(out_bytes / 1024, 1)

            self.state.output_path = final_out_path
            self.state.output_image = Image.open(final_out_path)
            self.state.output_data_uri = file_to_data_uri(final_out_path)

            self.state.metrics.result_width = out_w
            self.state.metrics.result_height = out_h
            self.state.metrics.result_kb = file_kb
            self.state.metrics.duration_seconds = elapsed

            self.state.status = ProcessingStatus.COMPLETED
            self.state.status_message = f"Completed in {elapsed}s · {out_w}×{out_h} px · {file_kb} KB"

        except Exception as exc:
            self.state.status = ProcessingStatus.ERROR
            self.state.status_message = f"Processing Error: {exc}"
            self.state.status_step = "Error during processing"
            self.state.status_subtext = str(exc)

        finally:
            self.state.is_processing = False
            self.notify_listeners()
