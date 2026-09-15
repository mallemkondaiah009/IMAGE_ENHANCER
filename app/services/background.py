"""
app/services/background.py
Advanced AI Background Removal Service with Sub-Pixel Edge Precision & Matting.
Extracts clean, studio-grade transparent cutouts while preserving 100% of the
original image pixels, resolution, colors, and textures (zero distortion, zero enhancement).
"""
import os
from functools import lru_cache
import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove as rembg_remove

_MODEL_PRIORITY = [
    "birefnet-general-lite",
    "birefnet-general",
    "isnet-general-use",
    "u2net",
]


@lru_cache(maxsize=1)
def get_rembg_session():
    """
    Initialise and cache the rembg inference session.
    Tries models in priority order; returns the first that loads successfully.
    """
    for model_name in _MODEL_PRIORITY:
        try:
            print(f"[+] Initialising rembg session with model '{model_name}'...")
            session = new_session(model_name)
            print(f"[+] rembg ready: '{model_name}'")
            return session
        except Exception as exc:
            print(f"[-] Could not load rembg model '{model_name}': {exc}")
    raise RuntimeError("No rembg model could be loaded. Check your onnxruntime installation.")


def refine_alpha_edges(mask: Image.Image) -> Image.Image:
    """
    Sub-pixel edge matting and anti-aliasing:
    - Preserves 100% solid foreground and 100% transparent background.
    - Eliminates micro-jagged stair-stepping along delicate curved prongs and facet boundaries.
    """
    blurred = mask.filter(ImageFilter.GaussianBlur(radius=0.8))
    m = np.array(mask, dtype=np.float32)
    b = np.array(blurred, dtype=np.float32)

    # Edge blend strictly in the transition contour zone (between 4 and 251)
    transition = (m > 3) & (m < 252)
    m[transition] = 0.3 * m[transition] + 0.7 * b[transition]
    m[m >= 252] = 255.0
    m[m <= 3] = 0.0

    return Image.fromarray(m.astype(np.uint8), mode="L")


def run_background_removal(
    img: Image.Image,
    output_path: str,
    target_size: tuple[int, int] = None,
    max_kb: int = None,
) -> tuple[int, int, int]:
    """
    Extracts 100% pure transparent cutout of the image using advanced rembg AI:
    - Extracts high-resolution alpha mask with post-process hole filling.
    - Applies sub-pixel edge refinement for flawless jewelry contours.
    - Preserves 100% of original image RGB values, colors, and resolution without any enhancement.
    Returns (width, height, file_size_bytes).
    """
    orig_w, orig_h = img.size
    session = get_rembg_session()

    # Extract high-precision alpha mask from BiRefNet
    mask = rembg_remove(
        img.convert("RGB"),
        session=session,
        only_mask=True,
        post_process_mask=True,
    )
    if mask.size != (orig_w, orig_h):
        mask = mask.resize((orig_w, orig_h), Image.Resampling.BILINEAR)

    # Apply sub-pixel edge anti-aliasing to eliminate aliasing and jagged fringes
    refined_mask = refine_alpha_edges(mask)

    # Combine original image RGB directly with the refined alpha mask
    # Guarantees 100.0% exact original pixels with zero alteration to subject RGB
    result = img.convert("RGBA")
    result.putalpha(refined_mask)

    # Save as pure lossless PNG preserving original colors and transparency
    result.save(output_path, format="PNG", optimize=True)
    actual_size_bytes = os.path.getsize(output_path)
    return orig_w, orig_h, actual_size_bytes
