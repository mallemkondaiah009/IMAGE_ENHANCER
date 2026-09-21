"""
app/components/animated_button.py
High-impact, eye-catching animated action button with glowing ambient shadows,
spring hover scaling, gradient transitions, and responsive state handling.
"""
from typing import Callable, Optional, List
import flet as ft


class AnimatedButton(ft.Container):
    def __init__(
        self,
        text: str,
        icon: Optional[str] = None,
        on_click: Optional[Callable] = None,
        gradient_colors: Optional[List[str]] = None,
        hover_gradient_colors: Optional[List[str]] = None,
        glow_color: str = "#2563EB55",
        text_color: str = "#FFFFFF",
        font_size: int = 12,
        border_radius: int = 4,
        padding: Optional[ft.Padding] = None,
        height: Optional[int] = 44,
        width: Optional[int] = None,
        expand: bool = False,
        disabled: bool = False,
    ):
        super().__init__()
        self._gradient_colors = gradient_colors or ["#2563EB", "#1D4ED8"]
        self._hover_gradient_colors = hover_gradient_colors or ["#3B82F6", "#2563EB"]
        self._glow_color = glow_color
        self._user_click = on_click
        self._text_str = text
        self._icon_name = icon

        # Sharp clean edges with subtle, non-blurry elevation
        self._normal_shadow = None
        self._hover_shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color="#00000060",
            offset=ft.Offset(0, 2),
        )

        # Micro-animations
        self.scale = 1.0
        self.animate_scale = ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC)
        self.animate = ft.Animation(180, ft.AnimationCurve.EASE_OUT)

        self.border_radius = border_radius
        self.padding = padding or ft.Padding.symmetric(vertical=10, horizontal=22)
        self.height = height
        self.width = width
        self.expand = expand
        self.mouse_cursor = ft.MouseCursor.CLICK

        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=self._gradient_colors,
        )
        self.shadow = self._normal_shadow

        # Content Row
        self.icon_widget = ft.Icon(icon, color=text_color, size=16) if icon else None
        self.text_widget = ft.Text(
            text,
            color=text_color,
            weight=ft.FontWeight.W_800,
            size=font_size,
        )

        controls = []
        if self.icon_widget:
            controls.append(self.icon_widget)
        controls.append(self.text_widget)

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=controls,
        )

        self.on_hover = self._handle_hover
        self.on_click = self._handle_click
        self.disabled = disabled

    @property
    def text(self) -> str:
        return self._text_str

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "disabled":
            self.opacity = 0.45 if value else 1.0
            self.scale = 1.0
            self.mouse_cursor = ft.MouseCursor.BASIC if value else ft.MouseCursor.CLICK
            if hasattr(self, "_normal_shadow"):
                self.shadow = None if value else self._normal_shadow

    def set_text(self, text: str) -> None:
        self._text_str = text
        self.text_widget.value = text
        if self.page:
            self.text_widget.update()

    def update_appearance(
        self,
        text: Optional[str] = None,
        icon: Optional[str] = None,
        gradient_colors: Optional[List[str]] = None,
        hover_gradient_colors: Optional[List[str]] = None,
        glow_color: Optional[str] = None,
    ) -> None:
        if text:
            self._text_str = text
            self.text_widget.value = text
        if icon and self.icon_widget:
            self.icon_widget.name = icon
        if gradient_colors:
            self._gradient_colors = gradient_colors
            self.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
                colors=gradient_colors,
            )
        if hover_gradient_colors:
            self._hover_gradient_colors = hover_gradient_colors
        if glow_color:
            self._glow_color = glow_color
            self._normal_shadow = None
            self._hover_shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000060",
                offset=ft.Offset(0, 2),
            )
            if not self.disabled:
                self.shadow = None
        try:
            if self.page:
                self.update()
        except Exception:
            pass

    def _handle_hover(self, e):
        if self.disabled:
            return
        is_hovered = e.data == "true"
        self.scale = 1.035 if is_hovered else 1.0
        self.shadow = self._hover_shadow if is_hovered else self._normal_shadow
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=self._hover_gradient_colors if is_hovered else self._gradient_colors,
        )
        try:
            if self.page:
                self.update()
        except Exception:
            pass

    def _handle_click(self, e):
        if self.disabled:
            return
        if self._user_click:
            self._user_click(e)
