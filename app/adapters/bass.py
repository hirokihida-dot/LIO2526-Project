"""Bass diffusion forecaster for launches without history (README §Modelos).

F(t) = (1 − e^(−(p+q)t)) / (1 + (q/p)·e^(−(p+q)t))
sales month t = m·(F(t) − F(t−1)) · seasonality_month, for 24 months.
CI month t: ±1,96 · (0,09 + 0,007 · t).
"""

from __future__ import annotations

import math

import pandas as pd

from app.core.domain.entities import ForecastFrame
from app.core.domain.params import (
    BASS_IC_BASE,
    BASS_IC_INCLINACION,
    CAMPANA,
    ESTACIONALIDAD_NEUTRA,
    FACTOR_ANALOGOS,
    MOTORIZACIONES,
    PESO_ANALOGOS,
    REPARTO_DEFAULT,
    REPARTO_PRECIO_REF,
    Z95,
)

EXPOSICION_PRECIO = 0.9
HORIZONTE_LANZAMIENTO = 24
MES_SALIDA_DEFAULT = pd.Timestamp("2026-11-01")


def bass_cumulative(t: float, p: float, q: float) -> float:
    """Cumulative adoption fraction F(t) of the Bass model at time t."""
    exponent = -(p + q) * t
    return (1.0 - math.exp(exponent)) / (1.0 + (q / p) * math.exp(exponent))


def market_size(
    segmento: str,
    motorizacion: str,
    precio: float,
    media_analogos: float | None = None,
) -> float:
    """m = base_segmento × f_motor × (precio_ref/precio)^0.9 (± mezcla análogos)."""
    try:
        base = REPARTO_DEFAULT[segmento]
        precio_ref = REPARTO_PRECIO_REF[segmento]
        factor = MOTORIZACIONES[motorizacion]["f"]
    except KeyError as exc:
        raise KeyError(f"Segmento o motorización desconocidos: {exc}") from exc
    m_base = base * factor * (precio_ref / precio) ** EXPOSICION_PRECIO
    if media_analogos is None:
        return m_base
    # Blend 50 % with media(существующие last 12 m of analogues) × 1.7.
    return PESO_ANALOGOS * m_base + (1.0 - PESO_ANALOGOS) * media_analogos * FACTOR_ANALOGOS


def ic_half_width(t: int) -> float:
    """Half width of the 95 % CI in month t (t starting at 1)."""
    return Z95 * (BASS_IC_BASE + BASS_IC_INCLINACION * t)


class ForecastBass:
    """Launch forecaster: monthly prevision for 24 months."""

    def forecast(self, parametros: dict) -> ForecastFrame:
        segmento = parametros["segmento"]
        motorizacion = parametros.get("motorizacion") or parametros.get("motor")
        campana = parametros["campaña"] if "campaña" in parametros else parametros["campana"]
        precio = float(parametros["precio"])

        m = market_size(
            segmento,
            motorizacion,
            precio,
            media_analogos=parametros.get("media_analogos"),
        )
        p = CAMPANA[campana]
        q = MOTORIZACIONES[motorizacion]["q"]

        estacionalidad = parametros.get("estacionalidad") or ESTACIONALIDAD_NEUTRA
        if not isinstance(estacionalidad, (list, tuple)) or len(estacionalidad) < (
            HORIZONTE_LANZAMIENTO
        ):
            if isinstance(estacionalidad, dict):
                entrada = [
                    float(estacionalidad.get(mes, 1.0))
                    for mes in range(1, HORIZONTE_LANZAMIENTO + 1)
                ]
            else:
                entrada = [1.0] * HORIZONTE_LANZAMIENTO
        else:
            entrada = [float(v) for v in estacionalidad[:HORIZONTE_LANZAMIENTO]]

        previsiones = []
        for t in range(1, HORIZONTE_LANZAMIENTO + 1):
            incremento = bass_cumulative(float(t), p, q) - bass_cumulative(
                float(t - 1), p, q
            )
            previsiones.append(m * incremento * entrada[t - 1])

        mes_salida = pd.Timestamp(parametros.get("mes_lanzamiento", MES_SALIDA_DEFAULT))
        periodos = pd.date_range(mes_salida, periods=HORIZONTE_LANZAMIENTO, freq="MS")

        return ForecastFrame(
            pd.DataFrame(
                {
                    "periodo": periodos,
                    "prevision": previsiones,
                    "ic_inf": [v - ic_half_width(t) for t, v in enumerate(
                        previsiones, start=1
                    )],
                    "ic_sup": [v + ic_half_width(t) for t, v in enumerate(
                        previsiones, start=1
                    )],
                }
            )
        )
