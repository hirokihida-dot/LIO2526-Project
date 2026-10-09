"""Common Plotly template (README «Gráficos») + CI band helper."""

from __future__ import annotations

import pandas as pd
from plotly import graph_objects as go

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Barlow, system-ui, sans-serif", size=12, color="#5d5d60"),
    margin=dict(l=54, r=14, t=24, b=30),
    hovermode="x unified",
    showlegend=False,
    xaxis=dict(showgrid=False, linecolor="rgba(29,31,32,.16)", ticks=""),
    yaxis=dict(gridcolor="#d4d4d7", zeroline=False, tickformat="~s", nticks=6),
    hoverlabel=dict(
        bgcolor="#1d2d3d", font_color="#ffffff", bordercolor="#1d2d3d"
    ),
)

CONFIG = {"displayModeBar": False}

_FILLCI = "rgba(181,217,253,.6)"


def ci_band(frame: pd.DataFrame, color: str | None = None) -> list[go.Scatter]:
    """Two traces drawing the shaded 95 % CI band (sup, then inf tonexty)."""
    line = dict(width=0, color=color) if color else dict(width=0)
    sup = go.Scatter(
        x=frame["periodo"],
        y=frame["ic_sup"],
        mode="lines",
        fill=None,
        line=line,
        hoverinfo="skip",
    )
    inf = go.Scatter(
        x=frame["periodo"],
        y=frame["ic_inf"],
        mode="lines",
        fill="tonexty",
        fillcolor=_FILLCI,
        line=dict(width=0),
        hoverinfo="skip",
    )
    return [sup, inf]
