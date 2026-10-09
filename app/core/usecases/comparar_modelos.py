"""Use case: model comparison (phases vs. naïve baseline)."""

from __future__ import annotations

import pandas as pd

from app.core.usecases.prever import evaluar_modelo
from app.core.ports.forecaster import Forecaster


def comparar_modelos(
    modelos: dict[str, Forecaster],
    hist: pd.DataFrame,
    ventana_backtest: int,
) -> pd.DataFrame:
    """Score each phase over the backtest window; sorted by best MAPE."""
    filas = []
    for nombre, modelo in modelos.items():
        metricas = evaluar_modelo(modelo, hist, ventana_backtest)
        filas.append({"modelo": nombre, **metricas})
    return pd.DataFrame(filas).sort_values("MAPE").reset_index(drop=True)
