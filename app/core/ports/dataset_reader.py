"""Port of the hexagon: validated reading of CSV/Excel sales history."""

from __future__ import annotations

import os
from typing import Protocol, runtime_checkable

from app.core.domain.entities import Dataset


@runtime_checkable
class DatasetReader(Protocol):
    """Validated load of a sales history file (CSV comma/«;» or Excel)."""

    def read(self, ruta: str | os.PathLike[str]) -> Dataset: ...
