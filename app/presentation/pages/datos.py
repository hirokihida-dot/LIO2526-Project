"""Page 01 · Carga de datos (/datos) — skeleton placeholder."""

from __future__ import annotations

import dash
from dash import html

from app.presentation.components.layout import page_header, placeholder_pantalla

dash.register_page(
    __name__,
    path="/datos",
    order=1,
    name="Carga de datos",
    title="01 · Carga de datos · SPV",
)

layout = html.Div(
    children=[
        page_header(
            kicker="01 · Carga de histórico",
            titulo="Carga de datos",
            subtitulo=(
                "Importa las ventas históricas por modelo de vehículo. El sistema "
                "valida el formato y agrega la serie a diaria, semanal o mensual."
            ),
        ),
        placeholder_pantalla(),
    ]
)
