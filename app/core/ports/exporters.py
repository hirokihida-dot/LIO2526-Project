"""Port of the hexagon: export of results (CSV «;» / JSON)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.core.domain.entities import ForecastFrame


@runtime_checkable
class Exporter(Protocol):
    """Exports a ForecastFrame (and metrics) focused on es-ES CSV or JSON."""

    def export_csv(self, frame: ForecastFrame, metricas: dict | None = None) -> str: ...

    def export_json(self, frame: ForecastFrame, metricas: dict | None = None) -> str: ...
