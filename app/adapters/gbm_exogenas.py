"""PENDING WORK — phase 3 forecaster: gradient boosting + exogenous vars. 

Intended with LightGBM: lags, rolling means, month, weekday, holidays,
`precio`, `promocion`, and optional sector matriculations; IC from
quantile regression (α 0.025 / 0.975) or conformal prediction. It is the
default active model per README («Modelo activo · Fase 3»). Never fabricate
results: any use raises until implemented.
"""

from __future__ import annotations

import pandas as pd

from app.core.domain.entities import ForecastFrame


class ForecasterGBM:
    """Placeholder for phase 3 — NOT implemented yet (honest stub)."""

    def __init__(self) -> None:
        raise NotImplementedError("Phase 3 (GBM) is not implemented yet")

    def forecast(self, hist: pd.DataFrame, horizonte: int) -> ForecastFrame:  # pragma: no cover
        """Unreachable: the constructor refuses instantiation until phase 3."""
        raise NotImplementedError("Phase 3 (GBM) is not implemented yet")
