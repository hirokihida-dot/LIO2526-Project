"""Use case: Bass launch without history (calibrated with analogues)."""

from __future__ import annotations

from app.core.domain.entities import ForecastFrame


def lanzar_sin_historico(motor_bass, parametros: dict) -> ForecastFrame:
    """Delegate to the Bass engine (injected adapter; port-like contract)."""
    return motor_bass.forecast(parametros)
