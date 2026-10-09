"""Tests for CSV/Excel dataset reading and validation."""

from pathlib import Path

import pandas as pd
import pytest

from app.adapters.csv_reader import CsvDatasetReader

REPO_ROOT = Path(__file__).resolve().parents[2]
EJEMPLO = REPO_ROOT / "data" / "ventas_ejemplo.csv"


class TestExampleDataset:
    def test_loads_example_csv_with_known_properties(self):
        ds = CsvDatasetReader().read(EJEMPLO)
        assert ds.meta["n_registers"] == 5480
        assert ds.meta["n_models"] == 5
        assert ds.meta["since"] == pd.Timestamp("2023-10-01")
        assert ds.meta["until"] == pd.Timestamp("2026-09-30")
        assert ds.meta["frequency"] == "D"

    def test_schema_columns_are_canonical(self):
        ds = CsvDatasetReader().read(EJEMPLO)
        assert list(ds.df.columns) == ["fecha", "sku", "unidades", "precio", "promocion"]
        assert pd.api.types.is_datetime64_any_dtype(ds.df["fecha"])

    def test_aggregate_weekly_monthly_without_nan(self):
        ds = CsvDatasetReader().read(EJEMPLO)
        for granularity in ("semanal", "mensual"):
            agg = ds.aggregate(granularity)
            assert not agg["unidades"].isna().any()


class TestSeparatorAndAliases:
    def test_semicolon_separated_csv_with_aliased_columns(self, tmp_path):
        content = (
            "date;producto;units;price;promo\n"
            "2025-01-06;A;3;100;0\n"
            "2025-01-06;B;4;200;1\n"
            "2025-01-07;A;5;100;0\n"
            "2025-01-07;B;6;200;0\n"
        )
        path = tmp_path / "aliased.csv"
        path.write_text(content, encoding="utf-8")
        ds = CsvDatasetReader().read(path)
        assert list(ds.df.columns) == ["fecha", "sku", "unidades", "precio", "promocion"]
        assert ds.meta["n_registers"] == 4
        assert ds.df.loc[0, "unidades"] == 3

    def test_missing_required_column_raises(self, tmp_path):
        path = tmp_path / "bad.csv"
        path.write_text("fecha,sku\n2025-01-06,A\n", encoding="utf-8")
        with pytest.raises(ValueError):
            CsvDatasetReader().read(path)

    def test_excel_reading_via_openpyxl(self, tmp_path):
        df = pd.DataFrame(
            {
                "fecha": pd.date_range("2025-01-01", periods=3),
                "sku": ["A"] * 3,
                "unidades": [1, 2, 3],
            }
        )
        path = tmp_path / "book.xlsx"
        df.to_excel(path, index=False)
        ds = CsvDatasetReader().read(path)
        assert ds.meta["n_registers"] == 3
