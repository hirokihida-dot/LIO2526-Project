"""Page 05 · Escenarios (/escenarios) — skeleton placeholder."""

from __future__ import annotations

import dash
from dash import html

from app.presentation.components.layout import page_header, placeholder_pantalla

dash.register_page(
    __name__,
    path="/escenarios",
    order=5,
    name="Escenarios",
    title="05 · Escenarios · SPV",
)

layout = html.Div(
    children=[
        page_header(
            kicker="05 · Escenarios",
            titulo="Escenarios",
            subtitulo=(
                "Palancas de precio, promoción, incentivo y estacionalidad sobre "
                "la previsión base."
            ),
        ),
        placeholder_pantalla(),
    ]
)
