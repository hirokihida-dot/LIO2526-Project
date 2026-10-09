"""Page 06 · Exportar (/exportar) — skeleton placeholder."""

from __future__ import annotations

import dash
from dash import html

from app.presentation.components.layout import page_header, placeholder_pantalla

dash.register_page(
    __name__,
    path="/exportar",
    order=6,
    name="Exportar",
    title="06 · Exportar · SPV",
)

layout = html.Div(
    children=[
        page_header(
            kicker="06 · Exportar",
            titulo="Exportar",
            subtitulo=(
                "Descarga de la previsión en CSV (separador «;») o JSON, con las "
                "métricas y el escenario si se marcan."
            ),
        ),
        placeholder_pantalla(),
    ]
)
