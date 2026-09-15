"""
app/theme/colors.py
Refined design tokens for LUMIÈRE Obsidian Black Studio aesthetic.
Pure deep black canvas, sleek dark card surfaces, high-contrast silver typography,
and glowing sapphire & emerald gemstone accents.
"""


class StudioColors:
    # ── Obsidian Black Backgrounds & Surfaces ─────────────────────────────────
    BG_WHITE           = "#000000"  # Pure Black canvas
    BG_DARK            = "#000000"  # Pure Black background
    CANVAS_BG          = "#05070D"  # Precision gallery canvas
    SURFACE_SLATE      = "#0B0F19"  # Main studio panels
    SURFACE_MUTED      = "#141B2D"  # Dark secondary surface
    CARD_BG            = "#0B0F19"  # Precision dark card background
    CARD_BG_HOVER      = "#151D2E"  # Elevated hover surface
    CARD_BORDER        = "#1E293B"  # Crisp hairline boundary
    CARD_BORDER_SUBTLE = "#161E2E"  # Muted boundary
    CARD_BORDER_GOLD   = "#3B82F6"  # Sapphire focus border
    CARD_BORDER_ACTIVE = "#3B82F6"  # Active focus border

    # ── Primary Branding Accents (Royal Sapphire) ─────────────────────────────
    GOLD_PRIMARY       = "#3B82F6"  # Electric Sapphire Blue
    GOLD_LIGHT         = "#60A5FA"  # Bright Blue
    GOLD_MUTED         = "#2563EB"  # Deep Sapphire
    GOLD_CHAMPAGNE     = "#93C5FD"  # Soft Sky Blue
    GOLD_CHIP_BG       = "#161F30"  # Soft blue chip background
    GOLD_CHIP_BORDER   = "#1E293B"  # Soft blue chip border

    # ── High-Contrast Silver / White Typography ───────────────────────────────
    TEXT_PRIMARY       = "#F8FAFC"  # Pure crisp White Slate-50
    TEXT_SECONDARY     = "#CBD5E1"  # Bright Silver Slate-200
    TEXT_MUTED         = "#94A3B8"  # Readable Muted Slate-400
    TEXT_ON_GOLD       = "#FFFFFF"  # Crisp White on action buttons
    TEXT_ON_DARK       = "#FFFFFF"

    # ── Functional & Status Indicators ────────────────────────────────────────
    SUCCESS_GREEN      = "#10B981"  # Emerald green active indicator
    SUCCESS_TEXT       = "#34D399"  # Bright emerald green
    SUCCESS_BG         = "#064E3B"  # Mint surface
    SUCCESS_BORDER     = "#059669"  # Mint border

    ERROR_RED          = "#F87171"  # Clean warning accent
    ERROR_BG           = "#450A0A"  # Soft warning surface
    ERROR_BORDER       = "#7F1D1D"  # Warning border

    # ── Action Button Tokens ──────────────────────────────────────────────────
    ENHANCE_BLUE_START = "#2563EB"  # Royal Sapphire
    ENHANCE_BLUE_END   = "#1D4ED8"
    ENHANCE_GLOW       = "#2563EB55"

    SAVE_GREEN_START   = "#059669"  # Jewel Emerald
    SAVE_GREEN_END     = "#047857"
    SAVE_GLOW          = "#05966955"

    # Compatibility Aliases
    COLOR_JET_BLACK    = "#000000"
    COLOR_WHITE_SMOKE  = "#F8FAFC"
    COLOR_GRANITE_GRAY = "#94A3B8"
    COLOR_ASH_GRAY     = "#CBD5E1"
