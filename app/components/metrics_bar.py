"""
app/components/metrics_bar.py
Bottom floating metrics bar displaying resolution, file size, and duration.
"""
import flet as ft
from app.models import StudioState
from app.theme import StudioColors


class MetricsBar(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = StudioColors.CARD_BG
        self.border = ft.Border.all(1.5, StudioColors.CARD_BORDER)
        self.border_radius = 4
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=14, color="#00000040", offset=ft.Offset(0, 4))
        self.padding = ft.Padding.symmetric(vertical=10, horizontal=20)
        self.visible = False

        self.stat_orig = ft.Text("—", size=12, weight=ft.FontWeight.W_800, color=StudioColors.TEXT_PRIMARY)
        self.stat_res = ft.Text("—", size=12, weight=ft.FontWeight.W_800, color=StudioColors.GOLD_MUTED)
        self.stat_file = ft.Text("—", size=12, weight=ft.FontWeight.W_800, color=StudioColors.TEXT_PRIMARY)
        self.stat_time = ft.Text("—", size=12, weight=ft.FontWeight.W_800, color=StudioColors.SUCCESS_TEXT)

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                self._build_metric_cell("ORIGINAL INPUT", self.stat_orig),
                ft.Container(width=1, height=28, bgcolor=StudioColors.CARD_BORDER),
                self._build_metric_cell("STUDIO RESOLUTION", self.stat_res),
                ft.Container(width=1, height=28, bgcolor=StudioColors.CARD_BORDER),
                self._build_metric_cell("FILE SIZE", self.stat_file),
                ft.Container(width=1, height=28, bgcolor=StudioColors.CARD_BORDER),
                self._build_metric_cell("PROCESSING TIME", self.stat_time),
            ],
        )

    def _build_metric_cell(self, title: str, text_ctl: ft.Text) -> ft.Column:
        return ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(title, size=10, color=StudioColors.TEXT_MUTED, weight=ft.FontWeight.W_800),
                text_ctl,
            ],
        )

    def update_from_state(self, state: StudioState) -> None:
        m = state.metrics
        if state.output_path and m.result_width > 0:
            self.visible = True
            self.stat_orig.value = f"{m.original_width} × {m.original_height} px ({m.original_kb} KB)"
            self.stat_res.value = f"{m.result_width} × {m.result_height} px (Enforced)"
            self.stat_file.value = f"{m.result_kb} KB (Master Quality)"
            self.stat_time.value = f"{m.duration_seconds}s GPU"
        elif state.input_path and m.original_width > 0:
            self.visible = True
            self.stat_orig.value = f"{m.original_width} × {m.original_height} px ({m.original_kb} KB)"
            self.stat_res.value = "Awaiting Enhancement"
            self.stat_file.value = "—"
            self.stat_time.value = "—"
        else:
            self.visible = False
