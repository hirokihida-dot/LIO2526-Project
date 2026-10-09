"""Tests for the phase 2 forecaster: Holt-Winters ETS (statsmodels)."""

import pandas as pd
import pytest

from app.adapters.holt_winters import HoltWinters


def monthly_hist(n=48, base=10.0, amplitude=6.0) -> pd.DataFrame:
    """Seasonal monthly series: base + amplitude * sin(month/12 * 2π)."""
    import math

    values = [
        base + amplitude * math.sin((i % 12) / 12 * 2 * math.pi) for i in range(n)
    ]
    return pd.DataFrame(
        {
            "fecha": pd.date_range("2022-01-01", periods=n, freq="MS"),
            "unidades": values,
        }
    )


@pytest.fixture(scope="module")
def forecast_6():
    hw = HoltWinters(seasonal_periods=12)
    return hw.forecast(monthly_hist(), 6)


class TestHoltWinters:
    def test_contract_and_horizon_length(self, forecast_6):
        assert list(forecast_6.columns) == ["periodo", "prevision", "ic_inf", "ic_sup"]
        assert len(forecast_6) == 6

    def test_all_values_finite(self, forecast_6):
        import math

        for col in ("prevision", "ic_inf", "ic_sup"):
            assert forecast_6[col].map(lambda v: math.isfinite(float(v))).all()

    def test_ci_brackets_point_forecast(self, forecast_6):
        assert (forecast_6["ic_inf"] <= forecast_6["prevision"]).all()
        assert (forecast_6["prevision"] <= forecast_6["ic_sup"]).all()

    def test_periods_are_month_starts_after_last_period(self, forecast_6):
        periods = pd.DatetimeIndex(forecast_6["periodo"])
        assert all(p.day == 1 for p in periods)
        assert periods[0] == pd.Timestamp("2026-01-01")  # hist ends 2025-12
        assert periods[-1] == pd.Timestamp("2026-06-01")
