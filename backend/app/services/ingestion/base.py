from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Generic, TypeVar

Record = TypeVar("Record")


class SourceAdapter(Generic[Record]):
    """Read source data and expose normalized records to planning services."""

    dataset_key: str

    def __init__(self, source_path: str | Path) -> None:
        self.source_path = Path(source_path)

    def load_raw(self) -> list[dict[str, Any]]:
        with self.source_path.open(encoding="utf-8") as source_file:
            payload = json.load(source_file)
        records = payload.get(self.dataset_key)
        if not isinstance(records, list):
            raise ValueError(f"Synthetic dataset is missing list: {self.dataset_key}")
        return records

    def load(self) -> list[Record]:
        return [self.normalize(record) for record in self.load_raw()]

    def normalize(self, record: dict[str, Any]) -> Record:
        return record  # type: ignore[return-value]
