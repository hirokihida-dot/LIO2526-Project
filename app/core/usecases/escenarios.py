"""Use case: scenario levers over the base forecast."""

from __future__ import annotations


def simular_escenario(motor_palancas, filas_por_sku: list[dict], palancas: dict) -> dict:
    """Apply levers per SKU and then sum across SKUs (dependency-injected)."""
    return motor_palancas.suma_por_sku(filas_por_sku, palancas)
