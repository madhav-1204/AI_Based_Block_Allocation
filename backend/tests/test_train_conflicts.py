from datetime import datetime, timezone

import pytest

from app.services.optimization.train_conflicts import find_train_conflicts, is_block_safe


def dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 9, 14, hour, minute, tzinfo=timezone.utc)


TRAIN = {"train_number": "12723", "corridor_id": "C102", "start_time": dt(10, 20), "end_time": dt(10, 25)}


def test_overlapping_train_is_hard_conflict() -> None:
    conflicts = find_train_conflicts("C102", dt(10), dt(11, 30), [TRAIN])
    assert len(conflicts) == 1
    assert conflicts[0].train_number == "12723"
    assert not is_block_safe("C102", dt(10), dt(11, 30), [TRAIN])


def test_different_corridor_is_ignored() -> None:
    other = {**TRAIN, "corridor_id": "C103"}
    assert is_block_safe("C102", dt(10), dt(11, 30), [other])


def test_touching_boundary_is_not_overlap() -> None:
    assert is_block_safe("C102", dt(10), dt(10, 20), [TRAIN])


def test_invalid_block_interval_is_rejected() -> None:
    with pytest.raises(ValueError, match="after"):
        find_train_conflicts("C102", dt(11), dt(10), [TRAIN])
