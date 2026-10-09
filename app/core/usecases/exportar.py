"""Use case: export of results (CSV «;» / JSON)."""

from __future__ import annotations

from app.core.ports.exporters import Exporter


def exportar(exportador: Exporter, frame, metricas: dict | None = None) -> str:
    """CSV («;», es-ES) by default; the exporter port owns the format."""
    return exportador.export_csv(frame, metricas=metricas)
