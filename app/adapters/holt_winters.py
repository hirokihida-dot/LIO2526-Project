"""Phase 2 forecaster: Holt-Winters ETS via statsmodels.

CI approximation (documented): ±1.96 × std of the in-sample residuals
(fitted − actual). README allows «El IC sale de simulación o de los residuos».
"""

from __future__ import annotations

import pandas as pd

from app.adapters.naive_stacional import _inferir_frecuencia
from app.core.domain.entities import ForecastFrame
from app.core.domain.params import Z95


class HoltWinters:
    """ϕ → ExponentialSmoothing(trend=add, damped_trend, seasonal=mul)."""

    def __init__(self, seasonal_periods: int) -> None:
        if seasonal_periods < 2:
            raise ValueError("seasonal_periods debe ser al menos 2")
        self.seasonal_periods = int(seasonal_periods)

    def forecast(self, hist: pd.DataFrame, horizonte: int) -> ForecastFrame:
        y = hist["unidades"].to_numpy(dtype=float)
        if horizonte < 1:
            raise ValueError("horizonte debe ser al menos 1")

        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        modelo = ExponentialSmoothing(
            y,
            trend="add",
            damped_trend=True,
            seasonal="mul",
            seasonal_periods=self.seasonal_periods,
            initialization_method="estimated",
        ).fit()
        fited = modelo.fittedvalues
        residuos = y - fited
        desviacion = float(
            residuos.std(ddof=0)
        )  # chart band half width
        half = Z95 * desviacion

        ajustado = modelo.forecast(horizonte)

        frecuencia = _inferir_frecuencia(hist["fecha"])
        futuro = pd.date_range(
            start=pd.Timestamp(hist["fecha"].iloc[-1]),
            periods=horizonte + 1,
            freq=frecuencia,
        )[1:]

        return ForecastFrame(
            pd.DataFrame(
                {
                    "periodo": futuro,
                    "prevision": [float(v) for v in ajustado],
                    "ic_inf": [float(v) - half for v in ajustado],
                    "ic_sup": [float(v) + half for v in ajustado],
                }
            )
        )
