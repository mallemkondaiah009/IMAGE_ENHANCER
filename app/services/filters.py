"""
app/services/filters.py
LUMIÈRE | Fine Jewelry Image Optimization Filters
Edge-Preserving, Color-Locked Gemstone & Metal Processing.

Prevents color bleeding and edge melting between gold and diamonds by:
1. Locking Hue (H) and Saturation (S) channels to prevent color migration.
2. Enhancing only high-frequency Luminance (V) with edge-safe thresholding.
3. Eliminating destructive halos and watercolor artifacts.
"""
from PIL import Image, ImageEnhance, ImageFilter


def apply_color_locked_clarity(
    img: Image.Image,
    radius: float = 1.0,
    percent: int = 70,
    threshold: int = 5,
) -> Image.Image:
    """
    Sharpens diamond facets and stone cuts strictly in the Luminance (V) channel.
    Hue and Saturation remain 100% locked so gold color cannot bleed into diamonds,
    and diamond highlights cannot blur over metal prongs.
    """
    img_rgb = img.convert("RGB")
    hsv = img_rgb.convert("HSV")
    h, s, v = hsv.split()

    # Gentle, edge-safe unsharp mask applied ONLY to luminance
    v_sharp = v.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))

    # Subtle micro-contrast on luminance only
    enhancer = ImageEnhance.Contrast(v_sharp)
    v_enhanced = enhancer.enhance(1.06)

    # Recombine with completely untouched Hue and Saturation
    clean_hsv = Image.merge("HSV", (h, s, v_enhanced))
    return clean_hsv.convert("RGB")


def apply_gemstone_clarity(img: Image.Image) -> Image.Image:
    """Facet clarity with zero color bleeding or prong shape melting."""
    return apply_color_locked_clarity(img, radius=0.9, percent=65, threshold=5)


def apply_metal_brilliance(img: Image.Image) -> Image.Image:
    """Polished metal luster with clean specular highlights and crisp prong tips."""
    return apply_color_locked_clarity(img, radius=1.1, percent=60, threshold=4)


def apply_luxury_dramatic(img: Image.Image) -> Image.Image:
    """Studio depth with preserved geometric boundaries."""
    img_rgb = img.convert("RGB")
    hsv = img_rgb.convert("HSV")
    h, s, v = hsv.split()

    v_sharp = v.filter(ImageFilter.UnsharpMask(radius=1.2, percent=80, threshold=4))
    enhancer = ImageEnhance.Contrast(v_sharp)
    v_enhanced = enhancer.enhance(1.12)

    return Image.merge("HSV", (h, s, v_enhanced)).convert("RGB")


def apply_clean_studio_white(img: Image.Image, threshold: int = 230) -> Image.Image:
    """
    Cleans studio backdrops to pure e-commerce white (#FFFFFF)
    using an edge-safe lookup table that leaves dark jewelry prongs intact.
    """
    img_rgb = img.convert("RGB")
    lut = []
    for i in range(256):
        if i < threshold:
            lut.append(i)
        else:
            factor = (i - threshold) / float(255 - threshold)
            val = int(i + (255 - i) * factor)
            lut.append(min(255, max(0, val)))
    return img_rgb.point(lut * 3)


def apply_jewelry_preset(img: Image.Image, preset: str = "natural") -> Image.Image:
    """Applies the chosen jewelry enhancement preset."""
    if preset == "gemstone":
        return apply_gemstone_clarity(img)
    elif preset == "metal":
        return apply_metal_brilliance(img)
    elif preset == "dramatic":
        return apply_luxury_dramatic(img)
    elif preset == "studio_white":
        sharp = apply_gemstone_clarity(img)
        return apply_clean_studio_white(sharp, threshold=230)
    else:
        # "natural" — 100% pure neural network reconstruction, zero post-filter distortion
        return img
