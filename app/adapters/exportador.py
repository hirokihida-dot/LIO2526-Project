"""Exporter implementation: CSV («;», es-ES numbers) and JSON.

It may import presentation.ui.formatting (allowed exception, README-approved)
to keep the es-ES number style consistent across the UI and the files.
"""

from __future__ import annotations

import json

import pandas as pd

from app.core.domain.entities import ForecastFrame

from app.presentation.ui.formatting import format_uds


def nombre_archivo(sku: str, granularidad: str, horizonte: int, formato: str) -> str:
    """Filename pattern: prevision_{sku}_{granularidad}_{horizonte}.{csv|json}."""
    if formato not in ("csv", "json"):
        raise ValueError(f"Formato no soportado: {formato}")
    return f"prevision_{sku}_{granularidad}_{horizonte}.{formato}"


def _es_es(value: float) -> str:
    """Raw CSV number: es-ES separators, up to one decimal, cleaned zeros."""
    texto = format_uds(float(value))
    # format_uds trims trailing zeros already; keep it symmetrical.
    return texto


def _metrica_es_es(value: float) -> str:
    """Metric value: str-comma form to avoid rounding (0,25 / 5,0)."""
    return str(value).replace(".", ",")


class Exportador:
    """Exporter port implementation for CSV «;» and JSON."""

    def export_csv(
        self, frame: ForecastFrame, metricas: dict | None = None
    ) -> str:
        lineas = ["periodo;prevision;ic_inf;ic_sup"]
        for row in frame.itertuples(index=False):
            periodo = pd.Timestamp(row.periodo).strftime("%Y-%m-%d")
            lineas.append(
                ";".join(
                    [
                        periodo,
                        _es_es(row.prevision),
                        _es_es(row.ic_inf),
                        _es_es(row.ic_sup),
                    ]
                )
            )
        if metricas:
            for clave, valor in metricas.items():
                lineas.append(f"{clave};{_metrica_es_es(valor)}")
        return "\n".join(lineas) + "\n"

    def export_json(
        self, frame: ForecastFrame, metricas: dict | None = None
    ) -> str:
        registros = []
        for row in frame.itertuples(index=False):
            registros.append(
                {
                    "periodo": pd.Timestamp(row.periodo).strftime("%Y-%m-%d"),
                    "prevision": float(row.prevision),
                    "ic_inf": float(row.ic_inf),
                    "ic_sup": float(row.ic_sup),
                }
            )
        salida: dict = {"prevision": registros}
        if metricas:
            salida["metricas"] = {k: float(v) for k, v in metricas.items()}
        return json.dumps(salida, ensure_ascii=False)


_EXPORTADOR = Exportador()
# Module-level conveniences expected by the tests/UI: functional API in front
# of the port implementation class.
export_csv = _EXPORTADOR.export_csv
export_json = _EXPORTADOR.export_json
