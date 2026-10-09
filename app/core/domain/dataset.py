"""Dataset entity: validated sales history + metadata.

Aggregation rules (README «Agregación»):
- Diaria: sin cambios.
- Semanal: semanas de lunes a domingo; solo semanas completas.
- Mensual: inicio de mes (MS).
"""

from __future__ import annotations

import pandas as pd

from app.core.domain.granularity import Granularidad, to_granularidad

REQUERIDAS = ("fecha", "sku", "unidades")
OPCIONALES = ("precio", "promocion")

_PERCENTIL_FRECUENCIA = {"D": (1,), "W": (7,), "MS": (28, 29, 30, 31)}


def _metric_frequency(dates: pd.Series) -> str:
    """Infer a coarse frequency tag from the unique dates of the dataset."""
    unique = pd.DatetimeIndex(sorted(pd.unique(dates)))
    if len(unique) < 2:
        return "D"
    deltas = pd.Series(unique[1:] - unique[:-1])
    delta_days = deltas.dt.days
    usual = int(delta_days.mode().iat[0])
    for tag, days in _PERCENTIL_FRECUENCIA.items():
        if usual in days:
            return tag
    return "D"


class Dataset:
    """Validated sales history. Requires fecha, sku, unidades (+ optional cols)."""

    def __init__(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise ValueError("Dataset requiere un pandas.DataFrame")
        if df.empty:
            raise ValueError("Dataset vacío: el histórico no tiene registros")
        faltantes = [c for c in REQUERIDAS if c not in df.columns]
        if faltantes:
            raise ValueError(f"Columnas obligatorias ausentes: {', '.join(faltantes)}")
        if not pd.api.types.is_datetime64_any_dtype(df["fecha"]):
            raise ValueError("La columna 'fecha' debe ser de tipo fecha/hora")

        self.df = df.reset_index(drop=True).copy()
        self.meta = self._build_meta()

    def _build_meta(self) -> dict:
        dates = self.df["fecha"]
        return {
            "n_registers": int(len(self.df)),
            "n_models": int(self.df["sku"].nunique()),
            "since": pd.Timestamp(dates.min()),
            "until": pd.Timestamp(dates.max()),
            "frequency": _metric_frequency(dates),
        }

    def aggregate(
        self, granularidad: Granularidad | str
    ) -> pd.DataFrame:
        """Aggregate unidades per period and SKU following the README rules."""
        g = to_granularidad(granularidad)
        if g is Granularidad.DIARIA:
            return self.df.rename(columns={"fecha": "periodo"})[
                ["periodo", "sku", "unidades"]
            ]
        if g is Granularidad.SEMANAL:
            return self._aggregate_periodo("W-MON", solo_completas=True)
        return self._aggregate_periodo("M", solo_completas=False)

    def _aggregate_periodo(self, freq: str, solo_completas: bool) -> pd.DataFrame:
        if freq == "W-MON":
            # ISO Monday weeks (Mon–Sun): to_period("W-MON") anchors Tue–Mon,
            # so the period key is the Monday floor of each date instead.
            offset = pd.to_timedelta(self.df["fecha"].dt.weekday, unit="D")
            work = self.df.assign(_periodo=self.df["fecha"] - offset)
        else:
            work = self.df.assign(_periodo=self.df["fecha"].dt.to_period(freq))
        if solo_completas:
            dias = work.groupby("_periodo")["fecha"].nunique()
            work = work[work["_periodo"].isin(dias[dias == 7].index)]
        out = work.groupby(["_periodo", "sku"], as_index=False)["unidades"].sum()
        if freq == "W-MON":
            out["periodo"] = out["_periodo"]
        else:
            out["periodo"] = out["_periodo"].dt.start_time
        return out[["periodo", "sku", "unidades"]]
