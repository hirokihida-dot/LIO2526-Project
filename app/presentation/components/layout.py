"""Root shell, sidebar and Industry blueprint components (header, cards, seg)."""

from __future__ import annotations

from dash import dcc, html, page_registry
from dash_iconify import DashIconify

NAV_ICONOS = {
    "/datos": "lucide:upload",
    "/": "lucide:chart-line",
    "/modelos": "lucide:layers",
    "/lanzamiento": "lucide:rocket",
    "/escenarios": "lucide:sliders-horizontal",
    "/exportar": "lucide:download",
}


def _item_nav(nombre: str, info: dict, numero: str) -> html.A:
    return html.A(
        className="nav-item",
        href=info["path"],
        style={
            "display": "flex",
            "alignItems": "center",
            "gap": "10px",
            "padding": "8px 14px",
            "textDecoration": "none",
            "fontSize": "14px",
            "color": "var(--color-neutral-300)",
        },
        children=[
            html.Span(
                numero,
                style={
                    "fontSize": "10px",
                    "color": "var(--color-accent-400)",
                    "letterSpacing": ".1em",
                },
            ),
            DashIconify(
                icon=NAV_ICONOS.get(info["path"], "lucide:circle"),
                width=18,
                height=18,
            ),
            html.Span(info["name"]),
        ],
    )


def sidebar(dataset_nombre: str = "ventas_ejemplo.csv") -> html.Div:
    """Fixed sidebar: brand, nav from page_registry, active dataset footer."""
    ordenados = sorted(page_registry, key=lambda k: page_registry[k]["order"])
    items = [
        _item_nav(nombre, page_registry[nombre], f"{i:02d}")
        for i, nombre in enumerate(ordenados, start=1)
    ]

    return html.Div(
        className="sidebar",
        style={
            "background": "var(--color-accent-900)",
            "color": "#fff",
            "height": "100vh",
            "position": "sticky",
            "top": 0,
            "display": "flex",
            "flexDirection": "column",
            "padding": "20px 12px",
            "gap": "6px",
        },
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "10px",
                    "marginBottom": "18px",
                    "padding": "0 8px",
                },
                children=[
                    html.Div(
                        "SPV",
                        style={
                            "width": "36px",
                            "height": "36px",
                            "border": "1px solid var(--color-accent-400)",
                            "display": "grid",
                            "placeItems": "center",
                            "fontSize": "12px",
                            "fontWeight": 600,
                            "color": "var(--color-accent-400)",
                        },
                    ),
                    html.Div(
                        children=[
                            html.Div(
                                "Previsión de ventas",
                                style={
                                    "fontFamily": "'Barlow Condensed', sans-serif",
                                    "fontSize": "19px",
                                    "fontWeight": 600,
                                    "lineHeight": 1.1,
                                },
                            ),
                            html.Div(
                                "AUTOMOCIÓN · V0.1",
                                style={
                                    "fontSize": "10px",
                                    "textTransform": "uppercase",
                                    "letterSpacing": ".1em",
                                    "color": "var(--color-accent-400)",
                                },
                            ),
                        ]
                    ),
                ],
            ),
            html.Nav(
                style={"display": "grid", "gap": "2px"},
                children=items,
            ),
            html.Div(style={"flex": 1}),
            html.Div(
                style={
                    "borderTop": "1px solid rgba(255,255,255,.08)",
                    "padding": "12px 8px 0",
                },
                children=[
                    html.Div(
                        "DATASET ACTIVO",
                        style={
                            "fontSize": "10px",
                            "letterSpacing": ".1em",
                            "textTransform": "uppercase",
                            "color": "var(--color-accent-400)",
                        },
                    ),
                    html.Div(dataset_nombre, style={"fontSize": "12px"}),
                    html.Div(
                        "5 modelos · 1.096 días",
                        style={
                            "fontSize": "11px",
                            "color": "var(--color-neutral-300)",
                        },
                    ),
                ],
            ),
        ],
    )


def card_blueprint(children, style: dict | None = None) -> html.Div:
    """Industry card with the 4 corner marks (`.card.blueprint`)."""
    return html.Div(
        className="card blueprint",
        style=style,
        children=[
            html.I(className="corner tl"),
            html.I(className="corner tr"),
            html.I(className="corner bl"),
            html.I(className="corner br"),
            *children,
        ],
    )


def page_header(kicker: str, titulo: str, subtitulo: str = "") -> html.Header:
    """Common page header: kicker, 42px condensed title, subtitle, side tags."""
    return html.Header(
        style={"display": "flex", "alignItems": "flex-start", "gap": "24px"},
        children=[
            html.Div(
                style={"flex": 1, "minWidth": 0},
                children=[
                    html.Div(
                        kicker,
                        style={
                            "fontSize": "11px",
                            "textTransform": "uppercase",
                            "letterSpacing": ".1em",
                            "color": "var(--color-accent-700)",
                        },
                    ),
                    html.H1(
                        titulo,
                        style={
                            "fontFamily": "'Barlow Condensed', sans-serif",
                            "fontSize": "42px",
                            "fontWeight": 600,
                            "margin": "4px 0 6px",
                            "lineHeight": 1,
                        },
                    ),
                    html.P(
                        subtitulo,
                        style={
                            "fontSize": "15px",
                            "color": "var(--color-neutral-700)",
                        },
                    ),
                ],
            ),
            html.Div(
                style={"display": "flex", "gap": "8px", "alignItems": "center"},
                children=[
                    html.Span(
                        className="tag tag-neutral", children=["Datos hasta 30 sep 2026"]
                    ),
                    html.Span(
                        className="tag tag-accent", children=["Modelo activo · Fase 3"]
                    ),
                ],
            ),
        ],
    )


def kpi_card(kicker: str, valor: str, unidad: str = "", meta: str = "") -> html.Div:
    """KPI card (kicker, used 40/600 value, unit, meta). Skeleton helper."""
    return card_blueprint(
        children=[
            html.Div(
                kicker,
                style={
                    "fontSize": "10px",
                    "textTransform": "uppercase",
                    "letterSpacing": ".1em",
                    "color": "var(--color-accent-700)",
                },
            ),
            html.Span(
                valor,
                style={
                    "fontFamily": "'Barlow Condensed', sans-serif",
                    "fontSize": "40px",
                    "fontWeight": 600,
                    "lineHeight": 1,
                },
            ),
            html.Span(unidad, style={"fontSize": "14px", "color": "var(--color-neutral-700)"}),
            html.Div(meta, style={"fontSize": "12px", "color": "var(--color-neutral-700)"}),
        ]
    )


def seg_control(opciones, valor_actual=None) -> html.Div:
    """Segmented control skeleton (`.seg` / `.seg-opt`)."""
    hijos = []
    for op in opciones:
        activo = op == valor_actual
        hijos.append(
            html.Button(
                op,
                className="seg-opt",
                style=(
                    {"background": "var(--color-accent)", "color": "var(--color-bg)"}
                    if activo
                    else {}
                ),
            )
        )
    return html.Div(className="seg", children=hijos)


def placeholder_pantalla(texto: str = "Pantalla prevista para una futura fase del proyecto.") -> html.Div:
    """The single placeholder card every skeleton page shows."""
    return card_blueprint(
        children=[
            html.P(texto, style={"color": "var(--color-neutral-700)"})
        ]
    )


def root_shell() -> html.Div:
    """Root layout: grid sidebar 232px + content minmax(0,1fr)."""
    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "232px minmax(0,1fr)",
            "minHeight": "100vh",
        },
        children=[
            sidebar(),
            html.Div(
                className="contenido",
                style={
                    "padding": "28px 36px 56px",
                    "display": "grid",
                    "gap": "28px",
                    "alignContent": "start",
                },
                children=[
                    dcc.Store(id="store-dataset"),
                    dcc.Store(id="store-filtros", storage_type="local"),
                    page_container_placeholder(),
                ],
            ),
        ],
    )


def page_container_placeholder():
    """Imported late so the module never shadows dash's page_container."""
    from dash import page_container

    return html.Main(
        id="contenido-pagina",
        style={"minWidth": 0},
        children=[page_container],
    )
