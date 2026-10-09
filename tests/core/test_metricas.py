"""Unit tests for domain metrics: MAPE, RMSE, IC coverage."""

import math

import pytest

from app.core.domain.metricas import ic_coverage, mape, rmse


class TestMape:
    def test_exact_value_on_hand_computed_arrays(self):
        y = [10.0, 10.0, 10.0, 10.0]
        yhat = [10.0, 10.0, 10.0, 20.0]
        assert mape(y, yhat) == pytest.approx(0.25)

    def test_zero_actuals_are_excluded_not_exploding(self):
        y = [0.0, 10.0, 10.0, 10.0]
        yhat = [99.0, 10.0, 10.0, 20.0]
        # Only 3 valid points: errors 0, 0, 1 -> mean of |e|/y = 1/3.
        assert mape(y, yhat) == pytest.approx(1.0 / 3.0)

    def test_perfect_forecast_is_zero(self):
        y = [5.0, 7.0, 9.0]
        assert mape(y, y) == pytest.approx(0.0)

    def test_all_zero_actuals_returns_zero(self):
        # Guard: no valid denominator at all -> defined 0.0, not NaN or error.
        assert mape([0.0, 0.0], [3.0, 4.0]) == pytest.approx(0.0)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            mape([1.0, 2.0], [1.0])


class TestRmse:
    def test_exact_value_on_hand_computed_arrays(self):
        y = [10.0, 10.0, 10.0, 10.0]
        yhat = [10.0, 10.0, 10.0, 20.0]
        assert rmse(y, yhat) == pytest.approx(5.0)

    def test_perfect_forecast_is_zero(self):
        assert rmse([3.0, 4.0], [3.0, 4.0]) == pytest.approx(0.0)

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            rmse([1.0], [1.0, 2.0])


class TestIcCoverage:
    def test_half_inside_gives_50_percent(self):
        y = [10.0, 10.0, 20.0, 20.0]
        ic_inf = [5.0, 5.0, 5.0, 5.0]
        ic_sup = [15.0, 15.0, 15.0, 15.0]
        assert ic_coverage(y, ic_inf, ic_sup) == pytest.approx(50.0)

    def test_none_inside_gives_0(self):
        assert ic_coverage([10.0, 10.0], [0.0, 0.0], [1.0, 1.0]) == pytest.approx(0.0)

    def test_all_inside_gives_100(self):
        assert ic_coverage([10.0], [9.0], [11.0]) == pytest.approx(100.0)

    def test_boundary_values_count_as_inside(self):
        # y exactly equal to a bound is inside the closed interval.
        assert ic_coverage([10.0], [10.0], [10.0]) == pytest.approx(100.0)

    def test_fractional_coverage(self):
        y = [10.0, 50.0, 10.0]
        assert ic_coverage(y, [9.0, 9.0, 9.0], [11.0, 11.0, 99.0]) == pytest.approx(
            100.0 * 2.0 / 3.0
        )

    def test_metric_domain_is_float_0_100_not_es_es_string(self):
        # Domain returns a raw float; es-ES formatting is a presentation concern.
        coverage = ic_coverage([1.0], [0.0], [2.0])
        assert isinstance(coverage, float)
        assert 0.0 <= coverage <= 100.0


def test_rmse_matches_direct_math_definition():
    errs = [1.0, -2.0, 2.0]
    y = [0.0, 0.0, 0.0]
    yhat = [-e for e in errs]
    expected = math.sqrt(sum(e * e for e in errs) / len(errs))
    assert rmse(y, yhat) == pytest.approx(expected)
