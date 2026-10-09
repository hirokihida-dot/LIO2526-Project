"""Use case: forecast phases + backtest → forecast and CI 95 %."""

from __future__ import annotations

import pandas as pd

from app.core.domain.entities import ForecastFrame
from app.core.domain.metricas import ic_coverage, mape, rmse
from app.core.ports.forecaster import Forecaster


def prever(modelo: Forecaster, hist: pd.DataFrame, horizonte: int) -> ForecastFrame:
    """Delegate the forecast to the injected phase (port Forecaster)."""
    return modelo.forecast(hist, horizonte)


def _partir_backtest(hist: pd.DataFrame, ventana: int) -> tuple[pd.DataFrame, pd.Series]:
    historico = hist.iloc[:-ventana]
    real = hist["unidades"].iloc[len(hist) - ventana : len(hist)]
    return historico, real


def evaluar_modelo(
    modelo: Forecaster, hist: pd.DataFrame, ventana_backtest: int
) -> dict:
    """Backtest: forecast the last `ventana_backtest` periods and score them."""
    historico, real = _partir_backtest(hist, ventana_backtest)
    prevision = modelo.forecast(historico, ventana_backtest)
    yhat = prevision["prevision"].tolist()
    ic_inf = prevision["ic_inf"].tolist()
    ic_sup = prevision["ic_sup"].tolist()
    y = real.tolist()
    return {
        "MAPE": mape(y, yhat),
        "RMSE": rmse(y, yhat),
        "cobertura_ic": ic_coverage(y, ic_inf, ic_sup),
    }
