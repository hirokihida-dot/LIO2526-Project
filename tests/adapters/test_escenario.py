"""Tests for the scenario lever engine (README «Escenarios»)."""

import pandas as pd
import pytest

from app.adapters.escenario_palancas import (
    MESES_PROMO,
    aplicar_palancas,
    acentuar_estacionalidad,
    factor_incentivo,
    factor_precio,
    factor_promo,
    suavizar_estacionalidad,
    suma_por_sku,
)


class TestSeasonLever:
    def test_suavizado_hacia_media_como_formula(self):
        vals = [0.86, 1.10, 1.22]
        media = sum(vals) / 3
        suave = suavizar_estacionalidad(vals)
        assert suave == pytest.approx([media + (v - media) * 0.5 for v in vals])

    def test_acento_multiplica_por_15(self):
        vals = [1.0, 0.8]
        assert acentuar_estacionalidad(vals) == pytest.approx([1.5, 1.2])


class TestPriceLever:
    def test_delta_negativo_sube_demanda(self):
        # Δprecio = −10 % → factor = 1 − 1,4 · (−0,10) = 1,14
        assert factor_precio(-0.10) == pytest.approx(1.14)

    def test_delta_cero_no_cambia(self):
        assert factor_precio(0.0) == pytest.approx(1.0)

    def test_delta_positivo_baja_demanda(self):
        assert factor_precio(0.10) == pytest.approx(0.86)


class TestPromoLever:
    def test_promo_multiplicador_en_meses_de_ventana(self):
        descuento = 0.10
        assert factor_promo(3, descuento) == pytest.approx(1 + 1.6 * descuento)  # Mar
        assert factor_promo(7, descuento) == pytest.approx(1 + 1.6 * descuento)  # Jul

    def test_promo_neutro_fuera_de_ventana(self):
        assert factor_promo(1, 0.10) == pytest.approx(1.0)   # Enero
        assert factor_promo(10, 0.10) == pytest.approx(1.0)  # Octubre

    def test_ventanas_son_mar_may_jun_jul_nov_dic(self):
        assert MESES_PROMO["Primavera"] == {3, 4, 5}
        assert MESES_PROMO["Verano"] == {6, 7}
        assert MESES_PROMO["Fin de año"] == {11, 12}

    def test_descuento_cero_no_cambia(self):
        assert factor_promo(7, 0.0) == pytest.approx(1.0)


class TestIncentiveLever:
    def test_electrico_114_y_resto_103(self):
        assert factor_incentivo(True) == pytest.approx(1.14)
        assert factor_incentivo(False) == pytest.approx(1.03)


class TestAplicarPalancas:
    def base(self):
        return {
            "unidades": 100.0,
            "precio": 20000.0,
            "mes": 6,  # Junio: dentro de la ventana Verano
            "electrico": False,
        }

    def test_palancas_se_multiplican(self):
        palancas = {
            "variacion_precio": -0.10,
            "descuento": 0.10,
            "ventana_promo": "Verano",
            "incentivo": True,
        }
        esperado = 100.0 * 1.14 * 1.16 * 1.03  # no eléctrico → 1,03
        res = aplicar_palancas(self.base(), palancas)
        assert res["unidades"] == pytest.approx(esperado)

    def test_ingreso_con_precio_y_descuento(self):
        palancas = {
            "variacion_precio": -0.10,
            "descuento": 0.10,
            "ventana_promo": "Verano",
        }
        res = aplicar_palancas(self.base(), palancas)
        assert res["ingreso"] == pytest.approx(
            res["unidades"] * 20000.0 * (1 - 0.10) * (1 - 0.10)
        )

    def test_sin_palancas_es_idéntico(self):
        res = aplicar_palancas(self.base(), {})
        assert res["unidades"] == pytest.approx(100.0)
        assert res["ingreso"] == pytest.approx(100.0 * 20000.0)

    def test_promo_fuera_de_ventana_no_aplica_descuento(self):
        base = self.base()
        base["mes"] = 1  # Enero: fuera de Verano
        res = aplicar_palancas(base, {"descuento": 0.15, "ventana_promo": "Verano"})
        assert res["unidades"] == pytest.approx(100.0)
        assert res["ingreso"] == pytest.approx(100.0 * 20000.0)

    def test_estacionalidad_acentuada(self):
        res = aplicar_palancas(self.base(), {"estacionalidad": "Acentuada"})
        assert res["unidades"] == pytest.approx(100.0 * 1.5)

    def test_incentivo_electrico_vs_resto(self):
        base = self.base()
        base["electrico"] = True
        res_elec = aplicar_palancas(base, {"incentivo": True})
        base["electrico"] = False
        res_resto = aplicar_palancas(base, {"incentivo": True})
        assert res_elec["unidades"] == pytest.approx(100.0 * 1.14)
        assert res_resto["unidades"] == pytest.approx(100.0 * 1.03)


class TestSumaEscenario:
    def test_por_sku_despues_suma(self):
        skus = [
            {"unidades": 60.0, "precio": 20000.0, "mes": 6, "electrico": False},
            {"unidades": 40.0, "precio": 34000.0, "mes": 6, "electrico": True},
        ]
        palancas = {"variacion_precio": -0.05, "descuento": 0.0, "ventana_promo": "Verano"}
        # Linealidad: aplicar palancas por SKU y sumar == sumar antes y aplicar.
        res_por_sku = suma_por_sku(skus, palancas)
        f = factor_precio(-0.05)  # no promo ni incentivo → solo precio
        assert res_por_sku["unidades"] == pytest.approx((60.0 + 40.0) * f)
