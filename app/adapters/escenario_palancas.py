"""Scenario lever engine (README «Escenarios», 12 months, monthly).

Levers apply PER SKU and then totals are SUMMED across SKUs.
All constants live in app.core.domain.params (single source).
"""

from __future__ import annotations

from app.core.domain.params import (
    ELASTICIDAD_PRECIO,
    ESTACIONALIDAD_ACENTO,
    ESTACIONALIDAD_SUAVIZADO,
    FACTOR_PROMO,
    INCENTIVO_ELECTRICO,
    INCENTIVO_RESTO,
    MESES_PROMO,
)


def suavizar_estacionalidad(valores) -> list[float]:
    """media + (v − media) · 0,5 (SUAVIZADO)."""
    media = sum(valores) / len(valores)
    return [media + (v - media) * ESTACIONALIDAD_SUAVIZADO for v in valores]


def acentuar_estacionalidad(valores) -> list[float]:
    """v · 1,5 (ACENTO)."""
    return [v * ESTACIONALIDAD_ACENTO for v in valores]


def factor_precio(variacion: float) -> float:
    """Demand multiplier: 1 − elasticidad · Δprecio."""
    return 1.0 - ELASTICIDAD_PRECIO * variacion


def factor_promo(mes: int, descuento: float) -> float:
    """Promo multiplier, active ONLY inside the chosen window months."""
    if descuento <= 0:
        return 1.0
    for ventana in MESES_PROMO.values():
        if mes in ventana:
            return 1.0 + FACTOR_PROMO * descuento
    return 1.0


def factor_incentivo(electrico: bool) -> float:
    """Public incentive: ×1,14 electric, ×1,03 everything else."""
    return INCENTIVO_ELECTRICO if electrico else INCENTIVO_RESTO


PALANCAS_DEFAULT = {
    "variacion_precio": 0.0,
    "descuento": 0.0,
    "ventana_promo": "Verano",
    "estacionalidad": "Normal",
    "incentivo": False,
}


def aplicar_palancas(fila: dict, palancas: dict) -> dict:
    """Apply every lever to one SKU/month row: units then revenue."""
    conf = {**PALANCAS_DEFAULT, **palancas}
    base = float(fila["unidades"])

    if conf["estacionalidad"] == "Acentuada":
        base *= ESTACIONALIDAD_ACENTO

    base *= factor_precio(float(conf["variacion_precio"]))
    base *= factor_promo(int(fila["mes"]), float(conf["descuento"]))
    if conf["incentivo"]:
        base *= factor_incentivo(bool(fila.get("electrico")))

    precio = float(fila["precio"]) * (1.0 + float(conf["variacion_precio"]))
    en_promo = factor_promo(int(fila["mes"]), float(conf["descuento"])) > 1.0
    ingreso = base * precio * (1.0 - float(conf["descuento"]) if en_promo else 1.0)

    return {"unidades": base, "ingreso": ingreso}


def suma_por_sku(filas: list[dict], palancas: dict) -> dict:
    """Levers PER SKU first, then sum units and revenue across SKUs."""
    unidades = 0.0
    ingreso = 0.0
    for fila in filas:
        resultado = aplicar_palancas(fila, palancas)
        unidades += resultado["unidades"]
        ingreso += resultado["ingreso"]
    return {"unidades": unidades, "ingreso": ingreso}
