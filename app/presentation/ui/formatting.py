"""es-ES number formatting (thousands «.», decimal «,», « %» with space)."""

from __future__ import annotations


def _formatear(value: float, decimales: int) -> str:
    """Internal: es-ES swap of the Python separators, trailing zeros trimmed."""
    texto = f"{value:,.{decimales}f}"
    if decimales and texto.endswith(".0"):
        texto = texto[:-2]
    return texto.replace(",", "«").replace(".", ",").replace("«", ".")


def format_uds(value: int | float) -> str:
    """Units formatted in es-ES: 1.234.567 / 1.234,5."""
    return _formatear(float(value), 1)


def format_pct(value: float) -> str:
    """Percent with space: «12,5 %» / «50 %»."""
    return f"{_formatear(float(value), 1)} %"
