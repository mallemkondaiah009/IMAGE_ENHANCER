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
    CutoutBackground,
    ViewMode,
    ProcessingStatus,
    ImageMetrics,
)
from app.services.enhancement import run_natural_enhancement
from app.services.background import run_background_removal, composite_cutout


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


def make_fast_preview_uri(path: str, max_dim: int = 1600) -> str:
    """
    Generates a fast, lightweight Data URI for instant UI display (< 10ms).
    - If file on disk is already a standard image (jpg/png/webp) <= 3MB:
      Directly base64 encodes the file bytes in < 2ms with zero compression CPU overhead.
    - If file is > 3MB (e.g. huge camera photo or raw PNG):
      Creates a high-quality downscaled JPEG thumbnail (max 1600px) in ~40ms,
      keeping the base64 payload under 500KB to ensure instant Flet UI updates.
    """
    if not os.path.exists(path):
        return ""
    try:
        size_bytes = os.path.getsize(path)
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        if size_bytes <= 3 * 1024 * 1024 and ext in ("jpg", "jpeg", "png", "webp"):
            mime = "image/webp" if ext == "webp" else ("image/png" if ext == "png" else "image/jpeg")
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("ascii")
            return f"data:{mime};base64,{encoded}"

        with Image.open(path) as img:
            orig_w, orig_h = img.size
            if max(orig_w, orig_h) > max_dim:
                ratio = max_dim / float(max(orig_w, orig_h))
                new_w = max(1, int(orig_w * ratio))
                new_h = max(1, int(orig_h * ratio))
                preview = img.resize((new_w, new_h), Image.Resampling.BILINEAR)
            else:
                preview = img.copy()

            buf = BytesIO()
            if preview.mode == "RGBA":
                preview.save(buf, format="PNG", optimize=False)
                mime = "image/png"
            else:
                preview.convert("RGB").save(buf, format="JPEG", quality=85)
                mime = "image/jpeg"
            encoded = base64.b64encode(buf.getvalue()).decode("ascii")
            return f"data:{mime};base64,{encoded}"
    except Exception as e:
        print(f"[-] Fast preview generation fallback error: {e}")
        return file_to_data_uri(path)


class StudioViewModel:
    def __init__(self):
        self.state = StudioState()
        self._listeners: list[Callable[[], None]] = []
        os.makedirs(settings.outputs_dir, exist_ok=True)

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

            with Image.open(path) as raw_im:
                orig_w, orig_h = raw_im.size
                img = raw_im.copy()
            orig_kb = round(os.path.getsize(path) / 1024, 1)

            self.state.input_path = path
            self.state.input_image = img
            self.state.input_data_uri = make_fast_preview_uri(path)

            # Reset batch mode when single image loaded
            self.state.is_batch = False
            self.state.batch_folder_path = None
            self.state.batch_folder_name = None
            self.state.batch_files = []
            self.state.batch_total = 0
            self.state.batch_current_index = 0
            self.state.batch_output_dir = None

            # Reset previous results
            self.state.output_path = None
            self.state.output_image = None
            self.state.output_data_uri = None
            self.state.cutout_alpha_image = None

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

    def load_folder(self, folder_path: str) -> bool:
        """Loads an entire folder of images for batch background removal."""
        try:
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                self.state.status = ProcessingStatus.ERROR
                self.state.status_message = f"Folder not found: {folder_path}"
                self.notify_listeners()
                return False

            valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
            all_entries = sorted(os.listdir(folder_path))
            files = [
                os.path.join(folder_path, f)
                for f in all_entries
                if os.path.splitext(f)[1].lower() in valid_exts and os.path.isfile(os.path.join(folder_path, f))
            ]

            if not files:
                self.state.status = ProcessingStatus.ERROR
                self.state.status_message = f"No supported images (.jpg, .png, .webp) found in: {os.path.basename(folder_path)}"
                self.notify_listeners()
                return False

            folder_name = os.path.basename(os.path.normpath(folder_path))
            # If folder with this name already exists in outputs, append _1, _2... to prevent duplicate collision
            out_folder_name = folder_name
            candidate_dir = os.path.join(settings.outputs_dir, out_folder_name)
            counter = 1
            while os.path.exists(candidate_dir) and os.listdir(candidate_dir):
                out_folder_name = f"{folder_name}_{counter}"
                candidate_dir = os.path.join(settings.outputs_dir, out_folder_name)

            self.state.is_batch = True
            self.state.batch_folder_path = folder_path
            self.state.batch_folder_name = out_folder_name
            self.state.batch_files = files
            self.state.batch_total = len(files)
            self.state.batch_current_index = 0
            self.state.batch_output_dir = candidate_dir

            # Load first image as preview on canvas
            first_path = files[0]
            with Image.open(first_path) as raw_im:
                orig_w, orig_h = raw_im.size
                img = raw_im.copy()
            orig_kb = round(os.path.getsize(first_path) / 1024, 1)

            self.state.input_path = first_path
            self.state.input_image = img
            self.state.input_data_uri = make_fast_preview_uri(first_path)

            self.state.output_path = None
            self.state.output_image = None
            self.state.output_data_uri = None
            self.state.cutout_alpha_image = None

            self.state.metrics = ImageMetrics(
                original_width=orig_w,
                original_height=orig_h,
                original_kb=orig_kb,
            )

            action_name = "enhance all images" if self.state.active_mode == EnhancementMode.ENHANCE else "remove BG for all"
            self.state.status = ProcessingStatus.IDLE
            self.state.status_message = f"Folder '{folder_name}' loaded ({len(files)} images). Click to {action_name}."
            self.state.view_mode = ViewMode.SPLIT
            self.notify_listeners()
            return True
        except Exception as exc:
            self.state.status = ProcessingStatus.ERROR
            self.state.status_message = f"Failed to load folder: {exc}"
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
            self.state.cutout_alpha_image = None
            if self.state.is_batch and self.state.batch_folder_name:
                action_name = "enhance all images" if mode == EnhancementMode.ENHANCE else "remove BG for all"
                self.state.status_message = f"Folder '{self.state.batch_folder_name}' loaded ({self.state.batch_total} images). Click to {action_name}."
            elif self.state.input_image:
                names = {
                    EnhancementMode.ENHANCE: "4x Super-Resolution Polish",
                    EnhancementMode.REMOVE_BG: "AI Studio Background Cutout",
                    EnhancementMode.COMBO: "Enhance + Cutout Combo",
                }
                pipeline_name = names.get(mode, mode.value)
                self.state.status_message = f"Ready to run {pipeline_name} on {os.path.basename(self.state.input_path) if self.state.input_path else 'loaded image'}."
            self.notify_listeners()

    def set_cutout_bg(self, bg: CutoutBackground) -> None:
        """Toggles between Studio White, Studio Black, and Transparent cutout in real time."""
        if self.state.cutout_bg != bg:
            self.state.cutout_bg = bg
            if self.state.cutout_alpha_image and self.state.output_path:
                # Instant re-composition in memory and save to disk
                composite = composite_cutout(
                    self.state.cutout_alpha_image,
                    bg_type=bg.value,
                    target_size=(settings.target_output_width, settings.target_output_height),
                )
                ext = ".png" if bg == CutoutBackground.TRANSPARENT else ".jpg"
                base, _ = os.path.splitext(self.state.output_path)
                new_path = base + ext
                if bg in (CutoutBackground.WHITE, CutoutBackground.BLACK):
                    composite.convert("RGB").save(new_path, format="JPEG", quality=98, optimize=True, subsampling=0)
                else:
                    composite.save(new_path, format="PNG", optimize=True)

                self.state.output_path = new_path
                self.state.output_image = composite
                self.state.output_data_uri = file_to_data_uri(new_path)
                file_kb = round(os.path.getsize(new_path) / 1024, 1)
                self.state.metrics.result_kb = file_kb
                names = {
                    CutoutBackground.WHITE: "Studio White (#FFFFFF)",
                    CutoutBackground.BLACK: "Studio Black (#000000)",
                    CutoutBackground.TRANSPARENT: "Transparent Cutout",
                }
                self.state.status_message = f"Applied {names.get(bg, bg.value)} · 2000×2000 px · {file_kb} KB"
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

    def export_image(self, destination_path: str) -> Optional[str]:
        """Copies or converts the processed output image to the destination with duplicate prevention."""
        if not self.state.output_path or not os.path.exists(self.state.output_path):
            return None
        try:
            # Prevent duplicate: if destination_path exists, append _1, _2...
            if os.path.exists(destination_path):
                stem, ext = os.path.splitext(destination_path)
                counter = 1
                candidate = f"{stem}_{counter}{ext}"
                while os.path.exists(candidate):
                    counter += 1
                    candidate = f"{stem}_{counter}{ext}"
                destination_path = candidate

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
            return destination_path
        except Exception as exc:
            self.state.status_message = f"Export failed: {exc}"
            self.notify_listeners()
            return None

    def export_folder(self, destination_parent: str) -> Optional[str]:
        """Copies the entire processed batch folder to destination_parent with duplicate prevention."""
        if not self.state.batch_output_dir or not os.path.exists(self.state.batch_output_dir):
            return None
        try:
            folder_name = self.state.batch_folder_name or "batch_output"
            # If user selected the folder itself as destination, avoid nesting
            if os.path.basename(os.path.normpath(destination_parent)).lower() == folder_name.lower():
                target_dir = destination_parent
            else:
                target_dir = os.path.join(destination_parent, folder_name)

            # Prevent duplicate folder: if target_dir already exists and has files, append _1, _2...
            if os.path.exists(target_dir) and os.listdir(target_dir):
                base_target = target_dir
                counter = 1
                candidate = f"{base_target}_{counter}"
                while os.path.exists(candidate) and os.listdir(candidate):
                    counter += 1
                    candidate = f"{base_target}_{counter}"
                target_dir = candidate

            shutil.copytree(self.state.batch_output_dir, target_dir, dirs_exist_ok=True)
            self.state.status_message = f"Downloaded full folder '{os.path.basename(target_dir)}' to {target_dir}"
            self.notify_listeners()
            return target_dir
        except Exception as exc:
            self.state.status_message = f"Failed to download folder: {exc}"
            self.notify_listeners()
            return None

    async def process_image(self) -> None:
        """Asynchronous execution pipeline running heavy models in worker threads."""
        if self.state.is_processing or not self.state.input_image or not self.state.input_path:
            return

        self.state.is_processing = True

        # Handle batch folder processing for both background removal and 4x enhancement
        if self.state.is_batch:
            if self.state.active_mode == EnhancementMode.ENHANCE:
                await self._process_batch_enhance()
                return
            elif self.state.active_mode == EnhancementMode.REMOVE_BG:
                await self._process_batch_remove_bg()
                return

        self.state.status = ProcessingStatus.PREPARING
        self.state.status_step = "Preparing high-res studio buffers..."
        self.state.status_subtext = f"Input resolution: {self.state.metrics.original_width}×{self.state.metrics.original_height} px"
        self.state.status_message = "[1/4] Preparing image buffers..."
        self.notify_listeners()
        await asyncio.sleep(0.05)

        req_id = uuid.uuid4().hex[:8]
        mode = self.state.active_mode
        start_time = time.time()

        orig_name = os.path.basename(self.state.input_path) if self.state.input_path else "image"
        stem, _ = os.path.splitext(orig_name)
        output_ext = "png" if (mode == EnhancementMode.REMOVE_BG and self.state.cutout_bg == CutoutBackground.TRANSPARENT) else "jpg"
        input_copy_path = os.path.join(settings.temp_dir, f"input_{req_id}.png")
        ncnn_temp_path = os.path.join(settings.temp_dir, f"ncnn_temp_{req_id}.png")

        if mode == EnhancementMode.ENHANCE:
            file_base = f"{stem}-enhanced_{req_id}"
        elif mode == EnhancementMode.REMOVE_BG:
            file_base = f"{stem}_{req_id}"
        else:
            file_base = f"{stem}-enhanced_{req_id}"

        final_out_path = os.path.join(settings.outputs_dir, f"{file_base}.{output_ext}")

        curr_img = self.state.input_image.copy()

        try:
            if mode == EnhancementMode.ENHANCE:
                self.state.status = ProcessingStatus.ENHANCING
                self.state.status_step = "Executing Real-ESRGAN Vulkan 4x Super-Resolution..."
                self.state.status_subtext = "Reconstructing diamond facets and gemstone crystal textures (2000×2000)"
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
                self.state.status_step = "Extracting Studio Background Cutout..."
                if self.state.cutout_bg == CutoutBackground.WHITE:
                    self.state.status_subtext = "BiRefNet cutout composited onto Pure Studio White (#FFFFFF)"
                elif self.state.cutout_bg == CutoutBackground.BLACK:
                    self.state.status_subtext = "BiRefNet cutout composited onto Pure Studio Black (#000000)"
                else:
                    self.state.status_subtext = "BiRefNet transparent alpha cutout (Lossless PNG)"
                self.state.status_message = f"[2/3] Extracting background cutout (2000×2000)..."
                self.notify_listeners()

                out_w, out_h, _, cutout_rgba = await asyncio.to_thread(
                    run_background_removal,
                    curr_img,
                    final_out_path,
                    (settings.target_output_width, settings.target_output_height),
                    None,
                    self.state.cutout_bg.value,
                )
                self.state.cutout_alpha_image = cutout_rgba

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
                self.state.status_step = "Phase 2: Studio Background Cutout..."
                self.state.status_subtext = "Isolating polished jewelry subject on pure studio background"
                self.state.status_message = "[3/4] Background cutout on 4x enhanced image..."
                self.notify_listeners()

                enhanced_img = Image.open(final_out_path).convert("RGB")
                out_w, out_h, _, cutout_rgba = await asyncio.to_thread(
                    run_background_removal,
                    enhanced_img,
                    final_out_path,
                    (settings.target_output_width, settings.target_output_height),
                    None,
                    self.state.cutout_bg.value,
                )
                self.state.cutout_alpha_image = cutout_rgba

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

    async def _process_batch_enhance(self) -> None:
        """Processes all images in the loaded batch folder with 4x Super-Resolution and writes them with identical names."""
        start_time = time.time()
        folder_name = self.state.batch_folder_name or "batch_output"
        out_dir = os.path.join(settings.outputs_dir, folder_name)
        os.makedirs(out_dir, exist_ok=True)
        self.state.batch_output_dir = out_dir

        total = len(self.state.batch_files)

        self.state.status = ProcessingStatus.ENHANCING
        self.state.status_step = f"Batch 4x Super-Resolution (0/{total})"
        self.state.status_subtext = f"Saving to outputs/{folder_name}/ with identical filenames"
        self.state.status_message = f"[0/{total}] Starting batch 4x Super-Resolution..."
        self.notify_listeners()
        await asyncio.sleep(0.05)

        try:
            for idx, file_path in enumerate(self.state.batch_files):
                orig_filename = os.path.basename(file_path)
                stem, ext = os.path.splitext(orig_filename)
                target_filename = orig_filename
                target_out_path = os.path.join(out_dir, target_filename)

                # Check for duplicate if multiple files share same name or already written
                if os.path.exists(target_out_path):
                    counter = 1
                    target_filename = f"{stem}_{counter}{ext}"
                    target_out_path = os.path.join(out_dir, target_filename)
                    while os.path.exists(target_out_path):
                        counter += 1
                        target_filename = f"{stem}_{counter}{ext}"
                        target_out_path = os.path.join(out_dir, target_filename)

                self.state.batch_current_index = idx + 1
                self.state.status = ProcessingStatus.ENHANCING
                self.state.status_step = f"Enhancing [{idx + 1}/{total}]: {orig_filename}"
                self.state.status_subtext = f"Output: outputs/{folder_name}/{target_filename} (2000×2000)"
                self.state.status_message = f"[{idx + 1}/{total}] 4x Super-Resolution on {orig_filename}..."
                self.notify_listeners()
                await asyncio.sleep(0.01)

                req_id = uuid.uuid4().hex[:6]
                input_copy_path = os.path.join(settings.temp_dir, f"batch_in_{req_id}.png")
                ncnn_temp_path = os.path.join(settings.temp_dir, f"batch_ncnn_{req_id}.png")

                with Image.open(file_path) as im:
                    curr_img = im.copy()

                out_w, out_h = await asyncio.to_thread(
                    run_natural_enhancement,
                    curr_img,
                    input_copy_path,
                    ncnn_temp_path,
                    target_out_path,
                )

                # Keep preview updated on canvas
                self.state.output_path = target_out_path
                self.state.output_image = Image.open(target_out_path)
                self.state.output_data_uri = file_to_data_uri(target_out_path)
                self.state.metrics.result_width = out_w
                self.state.metrics.result_height = out_h
                out_bytes = os.path.getsize(target_out_path)
                self.state.metrics.result_kb = round(out_bytes / 1024, 1)
                self.notify_listeners()

            elapsed = round(time.time() - start_time, 2)
            avg = round(elapsed / max(total, 1), 2)
            self.state.metrics.duration_seconds = elapsed
            self.state.status = ProcessingStatus.COMPLETED
            self.state.status_step = "Batch Enhancement Completed"
            self.state.status_subtext = f"Saved to outputs/{folder_name}/ ({total} images)"
            self.state.status_message = f"Done! All {total} images enhanced in outputs/{folder_name}/ in {elapsed}s (~{avg}s/image)"

        except Exception as exc:
            self.state.status = ProcessingStatus.ERROR
            self.state.status_message = f"Batch Enhancement Error: {exc}"
            self.state.status_step = "Batch enhancement interrupted"
            self.state.status_subtext = str(exc)

        finally:
            self.state.is_processing = False
            self.notify_listeners()

    async def _process_batch_remove_bg(self) -> None:
        """Processes all images in the loaded batch folder and writes them with identical names, preventing duplicate collisions."""
        start_time = time.time()
        folder_name = self.state.batch_folder_name or "batch_output"
        out_dir = os.path.join(settings.outputs_dir, folder_name)
        os.makedirs(out_dir, exist_ok=True)
        self.state.batch_output_dir = out_dir

        total = len(self.state.batch_files)
        bg_choice = self.state.cutout_bg.value

        self.state.status = ProcessingStatus.REMOVING_BG
        self.state.status_step = f"Batch Background Removal (0/{total})"
        self.state.status_subtext = f"Saving to outputs/{folder_name}/ with identical filenames"
        self.state.status_message = f"[0/{total}] Starting batch background removal..."
        self.notify_listeners()
        await asyncio.sleep(0.05)

        try:
            for idx, file_path in enumerate(self.state.batch_files):
                orig_filename = os.path.basename(file_path)
                stem, ext = os.path.splitext(orig_filename)

                # Maintain exact same filename; if transparent and source was not PNG, use PNG to preserve alpha
                if self.state.cutout_bg == CutoutBackground.TRANSPARENT:
                    target_filename = f"{stem}.png"
                else:
                    # White or Black BG preserves exact original filename
                    target_filename = orig_filename

                target_out_path = os.path.join(out_dir, target_filename)

                # Prevent duplicate filename collisions within the batch folder
                if os.path.exists(target_out_path):
                    target_stem, target_ext = os.path.splitext(target_filename)
                    counter = 1
                    target_filename = f"{target_stem}_{counter}{target_ext}"
                    target_out_path = os.path.join(out_dir, target_filename)
                    while os.path.exists(target_out_path):
                        counter += 1
                        target_filename = f"{target_stem}_{counter}{target_ext}"
                        target_out_path = os.path.join(out_dir, target_filename)

                self.state.batch_current_index = idx + 1
                self.state.status = ProcessingStatus.REMOVING_BG
                self.state.status_step = f"Processing [{idx + 1}/{total}]: {orig_filename}"
                self.state.status_subtext = f"Output: outputs/{folder_name}/{target_filename}"
                self.state.status_message = f"[{idx + 1}/{total}] Removing background from {orig_filename}..."
                self.notify_listeners()
                await asyncio.sleep(0.01)

                with Image.open(file_path) as im:
                    curr_img = im.copy()

                out_w, out_h, _, cutout_rgba = await asyncio.to_thread(
                    run_background_removal,
                    curr_img,
                    target_out_path,
                    (settings.target_output_width, settings.target_output_height),
                    None,
                    bg_choice,
                )

                # Keep preview updated on canvas
                self.state.output_path = target_out_path
                self.state.output_image = Image.open(target_out_path)
                self.state.output_data_uri = file_to_data_uri(target_out_path)
                self.state.cutout_alpha_image = cutout_rgba
                self.state.metrics.result_width = out_w
                self.state.metrics.result_height = out_h
                out_bytes = os.path.getsize(target_out_path)
                self.state.metrics.result_kb = round(out_bytes / 1024, 1)
                self.notify_listeners()

            elapsed = round(time.time() - start_time, 2)
            avg = round(elapsed / max(total, 1), 2)
            self.state.metrics.duration_seconds = elapsed
            self.state.status = ProcessingStatus.COMPLETED
            self.state.status_step = "Batch Completed"
            self.state.status_subtext = f"Saved to outputs/{folder_name}/ ({total} images)"
            self.state.status_message = f"Done! All {total} images saved to outputs/{folder_name}/ in {elapsed}s (~{avg}s/image)"

        except Exception as exc:
            self.state.status = ProcessingStatus.ERROR
            self.state.status_message = f"Batch Error: {exc}"
            self.state.status_step = "Batch processing interrupted"
            self.state.status_subtext = str(exc)

        finally:
            self.state.is_processing = False
            self.notify_listeners()

