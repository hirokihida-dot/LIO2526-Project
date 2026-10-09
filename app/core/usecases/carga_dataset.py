"""Use case: upload → validate → assign columns → aggregate.

Kept deliberately thin: the adapter (CsvDatasetReader) is injected so the
use case only depends on the port, never on the concrete implementation.

    from app.adapters.csv_reader import CsvDatasetReader
    citas = carga_dataset.leer_dataset(CsvDatasetReader(), "data/ventas_ejemplo.csv")
"""

from __future__ import annotations

from app.core.ports.dataset_reader import DatasetReader


def leer_dataset(lector: DatasetReader, ruta) -> object:
    """Delegate to the port implementation; validation happens in the adapter."""
    return lector.read(ruta)
