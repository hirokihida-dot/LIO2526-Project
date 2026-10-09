"""MAPE, RMSE y cobertura del IC 95 % (README §Modelos, métricas)."""

import math
from collections.abc import Sequence


def mape(y: Sequence[float], yhat: Sequence[float]) -> float:
    """Mean Absolute Percentage Error of the actuals y against forecast yhat.

    Guard (documented assumption): actuals equal to 0 have no defined
    percentage error and are excluded from the average. If no valid point
    remains, MAPE is defined as 0.0.
    """
    if len(y) != len(yhat):
        raise ValueError("mape: length mismatch between y and yhat")
    ratios = [abs(a - b) / a for a, b in zip(y, yhat, strict=True) if a != 0]
    if not ratios:
        return 0.0
    return sum(ratios) / len(ratios)


def rmse(y: Sequence[float], yhat: Sequence[float]) -> float:
    """Root Mean Squared Error: sqrt(mean((y - yhat)^2))."""
    if len(y) != len(yhat):
        raise ValueError("rmse: length mismatch between y and yhat")
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(y, yhat, strict=True)) / len(y))


def ic_coverage(
    y: Sequence[float], ic_inf: Sequence[float], ic_sup: Sequence[float]
) -> float:
    """Share of actuals inside the closed interval [ic_inf, ic_sup], in %.

    Domain value: float in 0..100 (es-ES rendering is a presentation concern).
    """
    if not len(y) == len(ic_inf) == len(ic_sup):
        raise ValueError("ic_coverage: length mismatch between y and CI bounds")
    inside = sum(
        lo <= v <= hi for v, lo, hi in zip(y, ic_inf, ic_sup, strict=True)
    )
    return 100.0 * inside / len(y)
