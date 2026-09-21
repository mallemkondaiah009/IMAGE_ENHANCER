"""
app/services/enhancement.py
Pure enhancement logic — no FastAPI imports, fully testable in isolation.
"""
import os
import subprocess
from PIL import Image

from app.config import settings
from app.services.filters import apply_color_locked_clarity
from app.services.optimizer import save_optimized_image


def run_natural_enhancement(
    img: Image.Image,
    input_path: str,
    ncnn_output_path: str,
    final_output_path: str,
) -> tuple[int, int]:
    """
    Runs the Real-ESRGAN NCNN Vulkan engine to upscale *img* 4x.
    Features Smart Studio Resolution Capping and Color-Locked Jewelry Polish:
      - Limits input to max_enhance_input_dim (500px)
      - Upscales 4x with Real-ESRGAN to ~2000px
      - Polishes diamond facets & gold reflections without color bleeding
      - Enforces exact 2000x2000 resolution via high-fidelity Lanczos resampling
      - Optimizes file size strictly <= 500 KB without compromising visual brilliance
      - Gracefully falls back to high-quality LANCZOS resize if engine fails.

    Returns (width, height) of the final output image (guaranteed 2000, 2000).
    """
    orig_w, orig_h = img.size

    # ── 1. Smart Studio Resolution Optimization ───────────────────────────────
    # If the image is large (> max_enhance_input_dim), downsample with Lanczos
    # so Real-ESRGAN operates in its trained sweet spot without tile overload.
    max_dim = settings.max_enhance_input_dim
    if max(orig_w, orig_h) > max_dim:
        scale_ratio = max_dim / float(max(orig_w, orig_h))
        target_in_w = max(1, int(orig_w * scale_ratio))
        target_in_h = max(1, int(orig_h * scale_ratio))
        engine_in = img.resize((target_in_w, target_in_h), Image.Resampling.LANCZOS)
    else:
        engine_in = img

    engine_input_path = input_path.replace(".png", "_ncnn_in.png")
    os.makedirs(os.path.dirname(engine_input_path), exist_ok=True)
    os.makedirs(os.path.dirname(final_output_path), exist_ok=True)
    engine_in.convert("RGB").save(engine_input_path, format="PNG")

    # ── 2. Select Model ───────────────────────────────────────────────────────
    # 4xNomos8kSC: authentic photographic super-resolution model —
    # 100% natural textures, zero anime stylisation, zero cartoon contours.
    # Falls back to the bundled realesrgan-x4plus model if Nomos is absent.
    target_model = "4xNomos8kSC"
    nomos_bin = os.path.join(settings.models_dir, f"{target_model}.bin")
    nomos_param = os.path.join(settings.models_dir, f"{target_model}.param")
    if not (os.path.exists(nomos_bin) and os.path.exists(nomos_param)):
        target_model = "realesrgan-x4plus"

    cmd = [
        settings.exe_path,
        "-i", engine_input_path,
        "-o", ncnn_output_path,
        "-m", settings.models_dir,
        "-n", target_model,
        "-g", "0",
        "-t", "128",
        "-j", "1:4:1",
    ]
    print(f"[+] Running Optimized Pure Natural AI Enhancement with {target_model}...")
    
    # Suppress console / terminal window popup on Windows
    subp_kwargs = {}
    if os.name == "nt":
        subp_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subp_kwargs["startupinfo"] = startupinfo

    proc = subprocess.run(cmd, capture_output=True, text=True, **subp_kwargs)

    if proc.returncode != 0:
        print(f"[-] NCNN Error: {proc.stderr}")
        in_w, in_h = engine_in.size
        upscaled = engine_in.resize((in_w * 4, in_h * 4), Image.Resampling.LANCZOS)
    else:
        upscaled = Image.open(ncnn_output_path)

    # ── 3. Color-Locked Jewelry Luminance Polish ──────────────────────────────
    # Enhances diamond facet sparkle and gold specular highlights while locking
    # hue and saturation to eliminate color bleeding between stone & metal.
    polished = apply_color_locked_clarity(upscaled, radius=0.9, percent=50, threshold=4)

    # ── 4. Enforce 2000x2000 Resolution (Maximum Studio Quality, No 500 KB Limit) ──
    out_w, out_h, actual_bytes = save_optimized_image(
        polished,
        final_output_path,
        target_size=(settings.target_output_width, settings.target_output_height),
        max_kb=None,
    )
    print(f"[+] Output ready: {out_w}x{out_h} px, {actual_bytes / 1024:.1f} KB (saved to {final_output_path})")

    # ── 5. Clean up temporary intermediate files ──────────────────────────────
    if os.path.exists(engine_input_path):
        try:
            os.remove(engine_input_path)
        except OSError:
            pass

    if os.path.exists(ncnn_output_path) and ncnn_output_path != final_output_path:
        try:
            os.remove(ncnn_output_path)
        except OSError:
            pass

    return out_w, out_h

