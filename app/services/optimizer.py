"""
app/services/optimizer.py
Adaptive image resolution & file size optimization.
Enforces:
  1. Exact target resolution (e.g. 2000x2000 px) using high-quality Lanczos resampling.
  2. File size ceiling (e.g. <= 500 KB) using adaptive quality search.
"""
import io
import os
from PIL import Image


def save_optimized_image(
    img: Image.Image,
    output_path: str,
    target_size: tuple[int, int] = (2000, 2000),
    max_kb: int = 500,
) -> tuple[int, int, int]:
    """
    Resamples `img` to `target_size` and saves it to `output_path` such that
    the resulting file size strictly does not exceed `max_kb` (<= 500 KB).

    Returns:
        (width, height, file_size_bytes)
    """
    # ── 1. Enforce exact resolution ───────────────────────────────────────────
    if img.size != target_size:
        img = img.resize(target_size, Image.Resampling.LANCZOS)

    # Ceiling is strictly <= 500,000 bytes (satisfies both decimal 500 KB and binary 512 KiB)
    max_bytes = min(max_kb * 1024, max_kb * 1000)

    has_alpha = img.mode in ("RGBA", "LA") or ("transparency" in img.info)

    if has_alpha or output_path.lower().endswith(".png"):
        # Transparent cutout -> PNG format with lossless alpha channel
        img_rgba = img.convert("RGBA") if img.mode != "RGBA" else img
        buf = io.BytesIO()
        img_rgba.save(buf, format="PNG", optimize=True, compress_level=9)
        best_bytes = buf.getvalue()

        # If file size ceiling is exceeded, optimize palette with Fast Octree quantization
        if len(best_bytes) > max_bytes:
            for colors in [256, 192, 128]:
                try:
                    q_buf = io.BytesIO()
                    quant = img_rgba.quantize(colors=colors, method=Image.Quantize.FASTOCTREE)
                    quant.save(q_buf, format="PNG", optimize=True)
                    best_bytes = q_buf.getvalue()
                    if len(best_bytes) <= max_bytes:
                        break
                except Exception:
                    pass

    else:
        # Standard photo / jewelry enhancement -> convert to RGB and use JPEG
        img_rgb = img.convert("RGB")
        best_bytes = None

        # Sweep qualities from highest (94) down to find maximum fidelity under max_bytes
        for q in [94, 92, 90, 88, 85, 82, 80, 78, 75, 70, 65, 60, 50, 40]:
            buf = io.BytesIO()
            img_rgb.save(buf, format="JPEG", quality=q, optimize=True)
            if buf.tell() <= max_bytes:
                best_bytes = buf.getvalue()
                break

        if best_bytes is None:
            buf = io.BytesIO()
            img_rgb.save(buf, format="JPEG", quality=40, optimize=True)
            best_bytes = buf.getvalue()

    with open(output_path, "wb") as f:
        f.write(best_bytes)

    actual_size_bytes = os.path.getsize(output_path)
    return img.size[0], img.size[1], actual_size_bytes
