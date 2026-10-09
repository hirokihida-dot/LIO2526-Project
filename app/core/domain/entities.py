"""Domain entities re-exports + forecast contract ForecastFrame.

The Dataset entity lives in `app.core.domain.dataset` and the Granularidad
enum in `app.core.domain.granularity`; both are re-exported here so the
«entities» module is the one-stop import point of the domain.
"""

from __future__ import annotations

import pandas as pd

from app.core.domain.dataset import Dataset
from app.core.domain.granularity import Granularidad

__all__ = ["Dataset", "ForecastFrame", "Granularidad", "CONTRACTO_COLUMNAS"]

CONTRACTO_COLUMNAS = ("periodo", "prevision", "ic_inf", "ic_sup")


class ForecastFrame(pd.DataFrame):
    """Forecast contract (README §Modelos).

    Every forecaster returns a DataFrame with exactly the columns
    `periodo, prevision, ic_inf, ic_sup` and a 95 % confidence interval:
    every row satisfies ic_inf <= prevision <= ic_sup.
    """

    def __init__(self, data=None, *args, **kwargs) -> None:
        super().__init__(data, *args, **kwargs)
        self.validate()

    def validate(self) -> None:
        faltantes = [c for c in CONTRACTO_COLUMNAS if c not in self.columns]
        if faltantes:
            raise ValueError(
                "ForecastFrame: faltan columnas del contrato: "
                f"{', '.join(faltantes)}"
            )
        if not self.empty and (
            (self["ic_inf"] > self["ic_sup"]).any()
        ):
            raise ValueError("ForecastFrame: hay filas con ic_inf > ic_sup")
