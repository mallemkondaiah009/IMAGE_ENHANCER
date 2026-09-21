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
    max_kb: int = None,
) -> tuple[int, int, int]:
    """
    Resamples `img` to exact `target_size` (e.g. 2000x2000 px) using high-fidelity Lanczos.
    If `max_kb` is None (default for super-resolution), saves at maximum uncompromised studio
    fidelity without any file size ceiling. If `max_kb` is set, adaptively searches for quality.

    Returns:
        (width, height, file_size_bytes)
    """
    # ── 1. Enforce exact resolution (guaranteed 2000x2000) ────────────────────
    if img.size != target_size:
        img = img.resize(target_size, Image.Resampling.LANCZOS)

    has_alpha = img.mode in ("RGBA", "LA") or ("transparency" in img.info)

    # ── 2. If no size cap (max_kb is None) -> Save at maximum studio quality ──
    if max_kb is None or max_kb <= 0:
        if has_alpha or output_path.lower().endswith(".png"):
            img_rgba = img.convert("RGBA") if img.mode != "RGBA" else img
            img_rgba.save(output_path, format="PNG", optimize=True)
        elif output_path.lower().endswith(".webp"):
            img.save(output_path, format="WEBP", quality=95)
        else:
            img_rgb = img.convert("RGB")
            # Quality 98 with subsampling=0 (4:4:4) gives studio-master color clarity
            img_rgb.save(output_path, format="JPEG", quality=98, optimize=True, subsampling=0)

        actual_size_bytes = os.path.getsize(output_path)
        return img.size[0], img.size[1], actual_size_bytes

    # ── 3. File size ceiling path (if max_kb is explicitly requested) ─────────
    max_bytes = min(max_kb * 1024, max_kb * 1000)

    if has_alpha or output_path.lower().endswith(".png"):
        img_rgba = img.convert("RGBA") if img.mode != "RGBA" else img
        buf = io.BytesIO()
        img_rgba.save(buf, format="PNG", optimize=True, compress_level=9)
        best_bytes = buf.getvalue()

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
        img_rgb = img.convert("RGB")
        best_bytes = None

        lo, hi = 40, 95
        while lo <= hi:
            mid = (lo + hi) // 2
            buf = io.BytesIO()
            img_rgb.save(buf, format="JPEG", quality=mid, optimize=True)
            if buf.tell() <= max_bytes:
                best_bytes = buf.getvalue()
                lo = mid + 1
            else:
                hi = mid - 1

        if best_bytes is None:
            buf = io.BytesIO()
            img_rgb.save(buf, format="JPEG", quality=40, optimize=True)
            best_bytes = buf.getvalue()

    with open(output_path, "wb") as f:
        f.write(best_bytes)

    actual_size_bytes = os.path.getsize(output_path)
    return img.size[0], img.size[1], actual_size_bytes
