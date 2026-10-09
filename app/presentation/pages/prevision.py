"""Page 02 · Previsión (/) — initial screen, skeleton placeholder."""

from __future__ import annotations

import dash
from dash import html

from app.presentation.components.layout import page_header, placeholder_pantalla

dash.register_page(
    __name__,
    path="/",
    order=2,
    name="Previsión",
    title="02 · Previsión · SPV",
)

layout = html.Div(
    children=[
        page_header(
            kicker="02 · Previsión",
            titulo="Previsión",
            subtitulo=(
                "Histórico y previsión con intervalo de confianza del 95 % por "
                "modelo, granularidad y horizonte."
            ),
        ),
        placeholder_pantalla(),
    ]
)
