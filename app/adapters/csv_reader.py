"""DatasetReader implementation: CSV (comma / semicolon) or Excel + aliases."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from app.core.domain.dataset import Dataset

# Column aliasing (README §Datos): canonical → accepted names.
ALIASES = {
    "fecha": ("fecha", "date"),
    "sku": ("sku", "modelo", "producto"),
    "unidades": ("unidades", "unid", "cant", "ventas", "units", "qty"),
    "precio": ("precio", "price"),
    "promocion": ("promocion", "promo"),
}
_CAPA_FORZOSA = ("fecha", "sku", "unidades")

_SEP_SNIFF_ROWS = 10


def _detectar_sep(path: Path) -> str:
    """Detect the separator with csv.Sniffer; fall back to ','."""
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        muestra = handle.read(_SEP_SNIFF_ROWS)
    try:
        dialect = csv.Sniffer().sniff(muestra, delimiters=",;\t")
        return dialect.delimiter
    except csv.Error:
        return ","


def _normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    destino = {}
    usadas: set[str] = set()
    for col in df.columns:
        nombre = str(col).strip().lower()
        encontrado = None
        for canonica, alias in ALIASES.items():
            if nombre in alias and canonica not in usadas:
                encontrado = canonica
                break
        if encontrado is not None:
            usadas.add(encontrado)
            destino[col] = encontrado
    normalizado = df.rename(columns=destino)
    faltantes = [c for c in _CAPA_FORZOSA if c not in normalizado.columns]
    if faltantes:
        raise ValueError(
            "Faltan columnas obligatorias: "
            f"{', '.join(faltantes)}. Encabezados válidos: fecha/date, "
            "sku/modelo/producto, unidades/unid/cant/ventas/units/qty."
        )
    extras = [
        c
        for c in ("precio", "promocion")
        if c in normalizado.columns
    ]
    return normalizado[["fecha", "sku", "unidades", *extras]]


class CsvDatasetReader:
    """Reads a sales history file into a validated Dataset."""

    def read(self, ruta: str | Path) -> Dataset:
        path = Path(ruta)
        if not path.exists():
            raise FileNotFoundError(f"No existe el archivo: {path}")
        if path.suffix.lower() in (".xlsx", ".xls"):
            bruto = pd.read_excel(path)
            sep = None
        else:
            sep = _detectar_sep(path)
            bruto = pd.read_csv(path, sep=sep)
        bruto = _normalizar_columnas(bruto)
        bruto["fecha"] = pd.to_datetime(bruto["fecha"], errors="raise")
        bruto["unidades"] = pd.to_numeric(bruto["unidades"], errors="raise")
        if "precio" in bruto.columns:
            bruto["precio"] = pd.to_numeric(bruto["precio"], errors="raise")
        if "promocion" in bruto.columns:
            bruto["promocion"] = pd.to_numeric(
                bruto["promocion"], errors="raise"
            )
        return Dataset(bruto)
