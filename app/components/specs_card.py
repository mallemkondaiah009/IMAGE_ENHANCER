"""
app/components/specs_card.py
Studio resolution & size enforcement specs card in pure white styling.
"""
import flet as ft
from app.config import settings
from app.theme import StudioColors


class SpecsCard(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = StudioColors.GOLD_CHIP_BG
        self.border = ft.Border.all(1, StudioColors.GOLD_CHIP_BORDER)
        self.border_radius = 12
        self.padding = 14

        self.content = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.VERIFIED, color=StudioColors.GOLD_PRIMARY, size=16),
                        ft.Text(
                            "Studio Output Standards Enforced",
                            size=12,
                            weight=ft.FontWeight.W_800,
                            color=StudioColors.GOLD_MUTED,
                        ),
                    ],
                ),
                self._build_spec_row("Resolution", f"Exactly {settings.target_output_width} × {settings.target_output_height} px (Lanczos)"),
                self._build_spec_row("File Size", f"Strictly ≤ {settings.max_output_file_size_kb} KB (Optimized Metadata)"),
                self._build_spec_row("Color Fidelity", "LAB Color-Locked Specular Fire & Clarity"),
            ],
        )

    def _build_spec_row(self, label: str, val: str) -> ft.Row:
        return ft.Row(
            spacing=6,
            controls=[
                ft.Container(width=4, height=4, bgcolor=StudioColors.GOLD_PRIMARY, border_radius=2),
                ft.Text(f"{label}: ", size=11, weight=ft.FontWeight.W_700, color=StudioColors.TEXT_SECONDARY),
                ft.Text(val, size=11, color=StudioColors.TEXT_MUTED),
            ],
        )
