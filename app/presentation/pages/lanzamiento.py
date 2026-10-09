"""Page 04 · Lanzamiento sin histórico (/lanzamiento) — skeleton placeholder."""

from __future__ import annotations

import dash
from dash import html

from app.presentation.components.layout import page_header, placeholder_pantalla

dash.register_page(
    __name__,
    path="/lanzamiento",
    order=4,
    name="Lanzamiento",
    title="04 · Lanzamiento · SPV",
)

layout = html.Div(
    children=[
        page_header(
            kicker="04 · Lanzamiento sin histórico",
            titulo="Lanzamiento",
            subtitulo=(
                "Curva de difusión de Bass para un modelo nuevo, calibrada con "
                "modelos análogos."
            ),
        ),
        placeholder_pantalla(),
    ]
)
