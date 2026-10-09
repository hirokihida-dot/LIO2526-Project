"""Phase 1 forecaster: seasonal naïve (ŷ_t = y_{t−m}) with residual CI.

CI assumption (documented, not in the spec): the 95 % interval is
prevision ± 1.96 × std of the in-sample residuals y_t − y_{t−m}. The spec
does not define a CI for phase 1, so this approximation keeps the forecast
contract (periodo, prevision, ic_inf, ic_sup) workable for charts/metrics.
"""

from __future__ import annotations

import pandas as pd

from app.core.domain.entities import ForecastFrame
from app.core.domain.params import Z95


def _inferir_frecuencia(fechas: pd.Series) -> str:
    fechas = pd.DatetimeIndex(pd.to_datetime(sorted(fechas)))
    if len(fechas) < 2:
        return "D"
    try:
        inferida = pd.infer_freq(fechas)
    except (ValueError, TypeError):
        inferida = None
    return inferida or "D"


class NaiveStacional:
    """ϕ → ŷ_t = y_{t−m}; future lags fall back on earlier forecasts."""

    def __init__(self, m: int) -> None:
        if m < 1:
            raise ValueError("m debe ser al menos 1")
        self.m = m

    def forecast(self, hist: pd.DataFrame, horizonte: int) -> ForecastFrame:
        y = hist["unidades"].to_numpy(dtype=float)
        n = len(y)
        if horizonte < 1:
            raise ValueError("horizonte debe ser al menos 1")

        # In-sample residuals (documented CI assumption).
        residuos = y[self.m :] - y[: n - self.m]
        desviacion = float(residuos.std(ddof=0)) if len(residuos) else 0.0
        half = Z95 * desviacion

        previsiones = []
        for i in range(horizonte):
            k = n + i - self.m
            previsiones.append(float(y[k]) if k < n else previsiones[k - n])

        periodo = hist["fecha"]
        frecuencia = _inferir_frecuencia(periodo)
        futuro = pd.date_range(
            start=pd.Timestamp(periodo.iloc[-1]), periods=horizonte + 1, freq=frecuencia
        )[1:]

        return ForecastFrame(
            pd.DataFrame(
                {
                    "periodo": futuro,
                    "prevision": previsiones,
                    "ic_inf": [v - half for v in previsiones],
                    "ic_sup": [v + half for v in previsiones],
                }
            )
        )
