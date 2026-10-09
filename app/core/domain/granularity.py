"""Granularidad de la serie de ventas (D / W-MON / MS)."""

from enum import Enum


class Granularidad(str, Enum):
    """Value string matches the es-ES UI tokens used by the filters."""

    DIARIA = "diaria"
    SEMANAL = "semanal"
    MENSUAL = "mensual"


def to_granularidad(value: "Granularidad | str") -> Granularidad:
    """Accept an enum member or its string value ('diaria'/'semanal'/'mensual')."""
    if isinstance(value, Granularidad):
        return value
    try:
        return Granularidad(str(value).lower().strip())
    except ValueError as exc:
        raise ValueError(f"Granularidad desconocida: {value!r}") from exc
