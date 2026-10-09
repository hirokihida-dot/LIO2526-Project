"""flask-caching wiring: SimpleCache + keys (hash_dataset, sku, granularidad).

Recalcular pesados (fase 3, backtesting) should be cached with a key made of
the dataset hash, the SKU and the granularity (README «Interacciones y estado»).
"""

from __future__ import annotations

import hashlib

from flask_caching import Cache

CONFIG_DEFAULT = {"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 300}

cache = Cache()


def init_cache(server) -> Cache:
    """Attach the cache to the Flask server behind the Dash app."""
    cache.init_app(server, config=CONFIG_DEFAULT)
    return cache


def hash_dataset(data: bytes | str) -> str:
    """Content hash of the dataset (bytes or the path of a parquet on disk)."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def clave_cache(hash_datos: str, sku: str, granularidad: str) -> str:
    """Cache key: (hash_dataset, sku, granularidad)."""
    return f"{hash_datos}:{sku}:{granularidad}"
