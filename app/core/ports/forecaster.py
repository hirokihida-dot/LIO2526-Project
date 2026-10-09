"""Ports of the hexagon: forecasting phases are interchangeable."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import pandas as pd

from app.core.domain.entities import ForecastFrame


@runtime_checkable
class Forecaster(Protocol):
    """Interchangeable forecasting phases (naive / ETS / GBM …)."""

    def forecast(self, hist: pd.DataFrame, horizonte: int) -> ForecastFrame: ...
