"""Tests for the Dataset entity and the aggregation rules (README «Agregación»)."""

import pandas as pd
import pytest

from app.core.domain.dataset import Dataset
from app.core.domain.granularity import Granularidad


def make_daily_df() -> pd.DataFrame:
    """2 SKUs over 4 complete weeks (Mon 2025-01-06 → Sun 2025-02-02)."""
    rows = []
    for sku in ("A", "B"):
        for day in range(28):
            rows.append(
                {
                    "fecha": pd.Timestamp("2025-01-06") + pd.Timedelta(days=day),
                    "sku": sku,
                    "unidades": float(day + 1),
                }
            )
    return pd.DataFrame(rows)


class TestEntityMeta:
    def test_registered_rows_models_range_frequency(self):
        ds = Dataset(make_daily_df())
        assert ds.meta["n_registers"] == 56
        assert ds.meta["n_models"] == 2
        assert ds.meta["since"] == pd.Timestamp("2025-01-06")
        assert ds.meta["until"] == pd.Timestamp("2025-02-02")
        assert ds.meta["frequency"] == "D"

    def test_missing_required_column_raises(self):
        df = make_daily_df().drop(columns=["unidades"])
        with pytest.raises(ValueError):
            Dataset(df)

    def test_empty_frame_raises(self):
        with pytest.raises(ValueError):
            Dataset(pd.DataFrame(columns=["fecha", "sku", "unidades"]))

    def test_non_datetime_fecha_raises(self):
        df = pd.DataFrame(
            {"fecha": ["a", "b"], "sku": ["A", "A"], "unidades": [1.0, 2.0]}
        )
        with pytest.raises(ValueError):
            Dataset(df)


class TestWeeklyAggregation:
    def test_periods_are_mondays(self):
        agg = Dataset(make_daily_df()).aggregate(Granularidad.SEMANAL)
        periods = pd.DatetimeIndex(agg["periodo"])
        assert all(p.weekday() == 0 for p in periods)
        assert len(periods) == 8  # 4 complete weeks × 2 SKUs
        assert periods.unique().shape[0] == 4

    def test_only_complete_weeks_are_kept(self):
        df = make_daily_df()
        # Drop the last day (Sunday 2025-02-02) → Jan 27 week becomes incomplete.
        df = df[df["fecha"] != pd.Timestamp("2025-02-02")]
        agg = Dataset(df).aggregate(Granularidad.SEMANAL)
        expected = {
            pd.Timestamp("2025-01-06"),
            pd.Timestamp("2025-01-13"),
            pd.Timestamp("2025-01-20"),
        }
        assert set(agg["periodo"]) == expected

    def test_units_are_summed_per_period_and_sku(self):
        agg = Dataset(make_daily_df()).aggregate(Granularidad.SEMANAL)
        sizes = agg.groupby("periodo").size()
        assert (sizes == 2).all()  # 2 SKUs per week
        first_week = agg[agg["periodo"] == pd.Timestamp("2025-01-06")].set_index("sku")
        # Day d has value d+1 → week 1 sum per sku = 7 + (0+...+7 accumulated)
        manual = sum(day + 1 for day in range(7))
        assert first_week.loc["A", "unidades"] == pytest.approx(float(manual))

    def test_accepts_string_granularity(self):
        agg = Dataset(make_daily_df()).aggregate("semanal")
        assert len(agg) == 8


class TestMonthlyAggregation:
    def test_periods_are_month_starts(self):
        agg = Dataset(make_daily_df()).aggregate(Granularidad.MENSUAL)
        assert set(agg["periodo"]) == {pd.Timestamp("2025-01-01"), pd.Timestamp("2025-02-01")}
        sizes = agg.groupby("periodo").size()
        # January complete month per SKU; February only 2 days but full-month
        # aggregation just groups by month (no completeness rule reads MENSUAL).
        assert (sizes == 2).all()

    def test_month_sums_match_manual(self):
        ds = Dataset(make_daily_df())
        manual = ds.df.groupby([ds.df["fecha"].dt.to_period("M"), "sku"])[
            "unidades"
        ].sum()
        agg = ds.aggregate(Granularidad.MENSUAL)
        assert agg["unidades"].sum() == pytest.approx(float(manual.sum()))


class TestDailyAggregation:
    def test_daily_passthrough_renames_fecha_to_periodo(self):
        agg = Dataset(make_daily_df()).aggregate(Granularidad.DIARIA)
        assert list(agg.columns) == ["periodo", "sku", "unidades"]
        assert len(agg) == 56
