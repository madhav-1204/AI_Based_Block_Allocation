from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrainConflict:
    train_number: str
    corridor_id: str
    train_start: datetime
    train_end: datetime


def intervals_overlap(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    """Return true only when intervals share time; touching boundaries are safe."""

    return max(left_start, right_start) < min(left_end, right_end)


def find_train_conflicts(corridor_id: str, block_start: datetime, block_end: datetime, trains: list[dict]) -> list[TrainConflict]:
    """Find movements that make a proposed maintenance block infeasible."""

    if block_end <= block_start:
        raise ValueError("Block end must be after block start")
    conflicts: list[TrainConflict] = []
    for train in trains:
        if train["corridor_id"] != corridor_id:
            continue
        if intervals_overlap(block_start, block_end, train["start_time"], train["end_time"]):
            conflicts.append(TrainConflict(train.get("train_number", "UNKNOWN"), corridor_id, train["start_time"], train["end_time"]))
    return conflicts


def is_block_safe(corridor_id: str, block_start: datetime, block_end: datetime, trains: list[dict]) -> bool:
    return not find_train_conflicts(corridor_id, block_start, block_end, trains)
