"""es-ES presentation formatting: miles «.», decimal «,», « %» with space."""

import pytest

from app.presentation.ui.formatting import format_pct, format_uds


class TestFormatUds:
    def test_miles_con_punto(self):
        assert format_uds(1234567) == "1.234.567"

    def test_caso_simple(self):
        assert format_uds(5) == "5"

    def test_decimal_con_coma(self):
        assert format_uds(1234.5) == "1.234,5"


class TestFormatPct:
    def test_decimal_coma_y_espacio(self):
        assert format_pct(12.5) == "12,5 %"

    def test_entero(self):
        assert format_pct(50) == "50 %"
