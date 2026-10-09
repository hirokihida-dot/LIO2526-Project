"""Page 03 · Comparativa de modelos (/modelos) — skeleton placeholder."""

from __future__ import annotations

import dash
from dash import html

from app.presentation.components.layout import page_header, placeholder_pantalla

dash.register_page(
    __name__,
    path="/modelos",
    order=3,
    name="Comparativa de modelos",
    title="03 · Comparativa de modelos · SPV",
)

layout = html.Div(
    children=[
        page_header(
            kicker="03 · Comparativa de modelos",
            titulo="Comparativa de modelos",
            subtitulo=(
                "MAPE, RMSE y cobertura del IC de cada fase sobre la ventana de "
                "backtest."
            ),
        ),
        placeholder_pantalla(),
    ]
)
