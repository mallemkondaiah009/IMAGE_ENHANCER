"""
app/theme/styles.py
Reusable widget styles with modern dark obsidian precision, pill geometry, and micro-animations.
"""
import flet as ft
from .colors import StudioColors


class StudioStyles:
    RADIUS_CARD = 14
    RADIUS_ITEM = 8
    RADIUS_CHIP = 16

    @staticmethod
    def primary_gold_button() -> ft.ButtonStyle:
        return ft.ButtonStyle(
            color={
                ft.ControlState.HOVERED: "#FFFFFF",
                "": StudioColors.TEXT_ON_GOLD,
            },
            bgcolor={
                ft.ControlState.HOVERED: "#1D4ED8",
                "": StudioColors.GOLD_PRIMARY,
            },
            shape=ft.RoundedRectangleBorder(radius=StudioStyles.RADIUS_ITEM),
            padding=ft.Padding.symmetric(vertical=14, horizontal=20),
            animation_duration=180,
        )

    @staticmethod
    def outlined_gold_button(active: bool = False) -> ft.ButtonStyle:
        active_color = "#60A5FA" if active else StudioColors.TEXT_SECONDARY
        active_border = "#3B82F6" if active else StudioColors.CARD_BORDER
        active_bg = "#1E293B" if active else ft.Colors.TRANSPARENT

        return ft.ButtonStyle(
            color={
                ft.ControlState.HOVERED: "#FFFFFF",
                "": active_color,
            },
            bgcolor={
                ft.ControlState.HOVERED: "#1E293B",
                "": active_bg,
            },
            side={
                ft.ControlState.HOVERED: ft.BorderSide(1.5, "#3B82F6"),
                "": ft.BorderSide(1.5 if active else 1.0, active_border),
            },
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.Padding.symmetric(horizontal=14, vertical=9),
            animation_duration=180,
        )

    @staticmethod
    def ghost_button() -> ft.ButtonStyle:
        return ft.ButtonStyle(
            color={
                ft.ControlState.HOVERED: "#FFFFFF",
                "": StudioColors.TEXT_SECONDARY,
            },
            bgcolor={
                ft.ControlState.HOVERED: "#1E293B",
                "": ft.Colors.TRANSPARENT,
            },
            side={
                ft.ControlState.HOVERED: ft.BorderSide(1, "#3B82F6"),
                "": ft.BorderSide(1, StudioColors.CARD_BORDER),
            },
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.Padding.symmetric(horizontal=16, vertical=10),
            animation_duration=180,
        )

    @staticmethod
    def dark_chip_button() -> ft.ButtonStyle:
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.HOVERED: "#334155",
                "": "#1E293B",
            },
            color={
                ft.ControlState.HOVERED: "#FFFFFF",
                "": StudioColors.TEXT_SECONDARY,
            },
            side={
                ft.ControlState.HOVERED: ft.BorderSide(1, "#3B82F6"),
                "": ft.BorderSide(1, StudioColors.CARD_BORDER),
            },
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.Padding.symmetric(horizontal=14, vertical=9),
            animation_duration=180,
        )
