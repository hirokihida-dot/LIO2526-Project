"""Tests for the exporter: CSV «;» / JSON with es-ES numbers."""

import json

import pandas as pd
import pytest

from app.adapters.exportador import export_csv, export_json, nombre_archivo
from app.core.domain.entities import ForecastFrame


def make_frame() -> ForecastFrame:
    return ForecastFrame(
        pd.DataFrame(
            {
                "periodo": pd.to_datetime(["2026-10-01", "2026-11-01"]),
                "prevision": [1234567.5, 10.0],
                "ic_inf": [1200000.0, 8.0],
                "ic_sup": [1270000.0, 12.0],
            }
        )
    )


class TestNombreArchivo:
    def test_patron_con_granularidad_y_horizonte(self):
        assert nombre_archivo("VEL", "mensual", 12, "csv") == (
            "prevision_VEL_mensual_12.csv"
        )

    def test_patron_json(self):
        assert nombre_archivo("NOR", "semanal", 26, "json") == (
            "prevision_NOR_semanal_26.json"
        )


class TestCsv:
    def test_separador_y_cabeceras(self):
        text = export_csv(make_frame())
        lines = text.strip().splitlines()
        assert lines[0] == "periodo;prevision;ic_inf;ic_sup"
        assert ";" in lines[1]
        # The decimal comma is allowed (es-ES); the field separator is «;».

    def test_numeros_es_es(self):
        text = export_csv(make_frame())
        assert "1.234.567,5" in text  # miles «.», decimal «,»

    def test_metricas_como_filas(self):
        text = export_csv(make_frame(), metricas={"MAPE": 0.25, "RMSE": 5.0})
        assert "MAPE;0,25" in text
        assert "RMSE;5,0" in text


class TestJson:
    def test_ida_y_vuelta(self):
        payload = json.loads(export_json(make_frame()))
        roundtrip = pd.DataFrame(payload["prevision"])
        assert list(roundtrip.columns) == ["periodo", "prevision", "ic_inf", "ic_sup"]
        assert len(roundtrip) == 2
        assert payload["prevision"][0]["prevision"] == pytest.approx(1234567.5)

    def test_metricas_incluidas(self):
        payload = json.loads(
            export_json(make_frame(), metricas={"MAPE": 0.25, "RMSE": 5.0})
        )
        assert payload["metricas"]["MAPE"] == pytest.approx(0.25)
        assert payload["metricas"]["RMSE"] == pytest.approx(5.0)
