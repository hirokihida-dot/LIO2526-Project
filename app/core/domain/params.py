"""Business constants (single source of truth) from README §Modelos."""

# Bases y precios de referencia por segmento (Bass diffusion market size).
REPARTO_DEFAULT = {
    "Compacto": 9500.0,
    "SUV": 12500.0,
    "Berlina": 6500.0,
    "Comercial": 5200.0,
}
REPARTO_PRECIO_REF = {
    "Compacto": 22000.0,
    "SUV": 33000.0,
    "Berlina": 31000.0,
    "Comercial": 28000.0,
}
SEGMENTOS = {
    name: {"base": REPARTO_DEFAULT[name], "precio_ref": REPARTO_PRECIO_REF[name]}
    for name in REPARTO_DEFAULT
}

# Motorización: factor de mercado (f) y coeficiente de imitación Bass (q).
MOTORIZACIONES = {
    "Gasolina": {"f": 1.0, "q": 0.30},
    "Híbrido": {"f": 1.08, "q": 0.36},
    "Eléctrico": {"f": 0.72, "q": 0.44},
}

# Campaña de lanzamiento: coeficiente de innovación Bass (p).
CAMPANA = {"Baja": 0.018, "Media": 0.03, "Alta": 0.05}
CAMPAÑA = CAMPANA  # en-es spelling alias used by the README vocabulary

# IC del mes t (Bass): ±1,96 · (0,09 + 0,007 · t).
Z95 = 1.96
BASS_IC_BASE = 0.09
BASS_IC_INCLINACION = 0.007

# Mezcla con análogos: 50 % base del segmento, 50 % media(análogos 12 m) × 1,7.
PESO_ANALOGOS = 0.5
FACTOR_ANALOGOS = 1.7

# Escenarios.
ELASTICIDAD_PRECIO = 1.4
FACTOR_PROMO = 1.6
INCENTIVO_ELECTRICO = 1.14
INCENTIVO_RESTO = 1.03
ESTACIONALIDAD_SUAVIZADO = 0.5
ESTACIONALIDAD_ACENTO = 1.5

# Ventanas de promoción por mes del año (1 = enero).
MESES_PROMO = {
    "Primavera": {3, 4, 5},
    "Verano": {6, 7},
    "Fin de año": {11, 12},
}

# Ventanas por granularidad: horizontes ofertados, backtest y ventana mostrada.
VENTANAS = {
    "diaria": {"horizontes": (30, 60, 90), "backtest": 30, "mostrar": 90},
    "semanal": {"horizontes": (12, 26, 52), "backtest": 12, "mostrar": 52},
    "mensual": {"horizontes": (6, 12, 18), "backtest": 6, "mostrar": 24},
}

# Naïve estacional: ciclo por granularidad.
NAIVE_M = {"diaria": 364, "semanal": 52, "mensual": 12}

# Estacionalidad mensual neutra (ene → dic). Sin datos históricos: 1,0.
ESTACIONALIDAD_NEUTRA = tuple(1.0 for _ in range(12))
