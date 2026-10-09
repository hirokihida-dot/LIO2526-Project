"""Tests for the phase 1 forecaster: seasonal naive."""

import pandas as pd
import pytest

from app.adapters.naive_stacional import NaiveStacional


def make_daily_hist(n=25) -> pd.DataFrame:
    """Deterministic daily series: unidades = day index (0-based)."""
    return pd.DataFrame(
        {
            "fecha": pd.date_range("2025-01-06", periods=n, freq="D"),
            "unidades": [float(i) for i in range(n)],
        }
    )


class TestNaiveForecaster:
    def test_forecasts_equal_lag_values_exactly(self):
        hist = make_daily_hist()
        halo = NaiveStacional(m=7)
        prev = halo.forecast(hist, 7)
        # yhat_t = y_{t−7}: first forecast = value 7 positions before the last.
        assert list(prev["prevision"]) == [18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0]

    def test_periods_continue_after_last_date(self):
        prev = NaiveStacional(m=7).forecast(make_daily_hist(), 3)
        assert list(prev["periodo"]) == list(
            pd.date_range("2025-01-31", periods=3, freq="D")
        )

    def test_contract_columns(self):
        prev = NaiveStacional(m=7).forecast(make_daily_hist(), 5)
        assert list(prev.columns) == ["periodo", "prevision", "ic_inf", "ic_sup"]
        assert len(prev) == 5

    def test_ci_contains_point_forecast_and_positive(self):
        prev = NaiveStacional(m=7).forecast(make_daily_hist(), 10)
        assert (prev["ic_inf"] <= prev["prevision"]).all()
        assert (prev["prevision"] <= prev["ic_sup"]).all()
        # Residual std > 0 → the point forecast must be strictly positive.
        assert (prev["prevision"] > 0).all()

    def test_ci_width_comes_from_in_sample_residual_std(self):
        # One jump at day 7 (index 7..24 = 200) → residuals are 100 then 0.
        hist = pd.DataFrame(
            {
                "fecha": pd.date_range("2025-01-06", periods=25, freq="D"),
                "unidades": [100.0] * 7 + [200.0] * 18,
            }
        )
        y = hist["unidades"].to_numpy(float)
        m = 7
        residuals = y[m:] - y[:-m]
        std = float(residuals.std(ddof=0))
        prev = NaiveStacional(m=m).forecast(hist, 5)
        half = 1.96 * std
        assert (prev["ic_sup"] - prev["prevision"]).eq(half).all()
        assert (prev["prevision"] - prev["ic_inf"]).eq(half).all()

    def test_smooth_series_gives_zero_width_ci(self):
        hist = pd.DataFrame(
            {
                "fecha": pd.date_range("2025-01-06", periods=25, freq="D"),
                "unidades": [10.0 + (i % 7) * 2 for i in range(25)],
            }
        )
        # Periodic with period 7 → residuals y_t - y_{t-7} are exactly 0.
        prev = NaiveStacional(m=7).forecast(hist, 3)
        assert (prev["ic_inf"] == prev["ic_sup"]).all()
