"""Tests for the Bass diffusion launch forecaster (README «Lanzamiento»)."""

import math

import pytest

from app.adapters.bass import (
    ForecastBass,
    market_size,
    ic_half_width,
    bass_cumulative,
)
from app.core.domain.params import (
    CAMPAÑA,
    MOTORIZACIONES,
    REPARTO_DEFAULT,
    REPARTO_PRECIO_REF,
)

import pandas as pd


HZ = {"campaña": "Media", "motor": "Eléctrico", "segmento": "SUV", "precio": 39900.0}


class TestBassMathematics:
    def test_cumulative_curve_matches_formula_by_hand(self):
        p, q = CAMPAÑA["Media"], MOTORIZACIONES["Eléctrico"]["q"]
        for t in (0.0, 1.0, 3.0, 12.0):
            exponent = -(p + q) * t
            expected = (1 - math.exp(exponent)) / (
                1 + (q / p) * math.exp(exponent)
            )
            assert bass_cumulative(t, p, q) == pytest.approx(expected)

    def test_t0_is_zero_and_curve_increases(self):
        assert bass_cumulative(0.0, 0.03, 0.36) == pytest.approx(0.0)
        vals = [bass_cumulative(t, 0.03, 0.36) for t in range(25)]
        for a, b in zip(vals, vals[1:]):
            assert b > a

    def test_market_size_known_value_suv_electric(self):
        m = market_size("SUV", "Eléctrico", precio=39900.0)
        expected = REPARTO_DEFAULT["SUV"] * MOTORIZACIONES["Eléctrico"]["f"] * (
            REPARTO_PRECIO_REF["SUV"] / 39900.0
        ) ** 0.9
        assert m == pytest.approx(expected)

    def test_analogues_blend_is_half_and_half(self):
        solo = market_size("SUV", "Eléctrico", 39900.0)
        con_analogos = market_size("SUV", "Eléctrico", 39900.0, media_analogos=200.0)
        esperado = 0.5 * solo + 0.5 * 200.0 * 1.7
        assert con_analogos == pytest.approx(esperado)

    def test_unknown_segment_raises(self):
        with pytest.raises(KeyError):
            market_size("Furgón", "Eléctrico", 20000.0)


# CI width: README says IC del mes t = ±1,96 * (0,09 + 0,007 * t) — half width per month.

def _previsiona() -> pd.DataFrame:
    return ForecastBass().forecast(HZ)


class TestForecastOutput:
    def test_horizon_is_24_months(self):
        frame = _previsiona()
        assert len(frame) == 24

    def test_periods_are_month_starts_from_nov_2026(self):
        frame = _previsiona()
        periodos = pd.DatetimeIndex(frame["periodo"])
        assert periodos[0] == pd.Timestamp("2026-11-01")
        assert periodos[-1] == pd.Timestamp("2028-10-01")

    def test_ci_width_matches_hand_computed_formula(self):
        frame = _previsiona()
        for i, row in enumerate(frame.itertuples(), start=1):
            width = row.ic_sup - row.ic_inf
            assert width == pytest.approx(2 * 1.96 * (0.09 + 0.007 * i))

    def test_ci_brackets_point_forecast(self):
        frame = _previsiona()
        assert (frame["ic_inf"] <= frame["prevision"]).all()
        assert (frame["prevision"] <= frame["ic_sup"]).all()

    def test_contract_columns(self):
        frame = _previsiona()
        assert list(frame.columns) == ["periodo", "prevision", "ic_inf", "ic_sup"]

    def test_total_sales_match_m_curve_integration(self):
        frame = _previsiona()
        total = frame["prevision"].sum()
        m = market_size("SUV", "Eléctrico", 39900.0)
        # With constant seasonality (default ones), sum of monthly sales
        # telescopes to m * (F(24) - F(0)) if no seasonality applied.
        p = CAMPAÑA["Media"]
        q = MOTORIZACIONES["Eléctrico"]["q"]
        assert total == pytest.approx(m * bass_cumulative(24.0, p, q), rel=1e-6)
