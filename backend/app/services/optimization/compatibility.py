from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CompatibilityResult:
    compatible: bool
    reasons: tuple[str, ...]
    separate_duration_minutes: int
    coordinated_duration_minutes: int
    savings_minutes: int


def _overlap(left_start: float, left_end: float, right_start: float, right_end: float) -> bool:
    return max(left_start, right_start) < min(left_end, right_end)


def _time_overlap(left_start: datetime, left_end: datetime, right_start: datetime, right_end: datetime) -> bool:
    return max(left_start, right_start) < min(left_end, right_end)


def check_compatibility(
    tasks: list[dict],
    *,
    block_type: str,
    max_duration_minutes: int,
    resources_available: set[str] | None = None,
    conflicting_trains: list[dict] | None = None,
    block_start: datetime | None = None,
    block_end: datetime | None = None,
) -> CompatibilityResult:
    """Evaluate whether tasks may safely share one protected block."""

    if not tasks:
        return CompatibilityResult(False, ("No tasks provided",), 0, 0, 0)
    reasons: list[str] = []
    corridors = {task["corridor_id"] for task in tasks}
    if len(corridors) != 1:
        return CompatibilityResult(False, ("Tasks are on different corridors",), sum(task["estimated_duration_minutes"] for task in tasks), 0, 0)
    location_start = max(task["location_start"] for task in tasks)
    location_end = min(task["location_end"] for task in tasks)
    if location_start >= location_end:
        return CompatibilityResult(False, ("Task locations do not overlap",), sum(task["estimated_duration_minutes"] for task in tasks), 0, 0)
    reasons.append("Same corridor and overlapping location")
    if any(task["required_block_type"] not in {block_type, "COMBINED_BLOCK"} for task in tasks):
        return CompatibilityResult(False, ("Block type is not supported by every task",), sum(task["estimated_duration_minutes"] for task in tasks), 0, 0)
    durations = [int(task["estimated_duration_minutes"]) for task in tasks]
    coordinated = max(durations)
    separate = sum(durations)
    if coordinated > max_duration_minutes:
        return CompatibilityResult(False, ("Coordinated duration exceeds block limit",), separate, coordinated, 0)
    if resources_available is not None:
        required = {resource for task in tasks for resource in str(task.get("required_resources", "")).split(",") if resource}
        if not required.issubset(resources_available):
            return CompatibilityResult(False, ("Required resources are unavailable",), separate, coordinated, 0)
    if conflicting_trains and block_start and block_end:
        for train in conflicting_trains:
            if train["corridor_id"] == next(iter(corridors)) and _time_overlap(block_start, block_end, train["start_time"], train["end_time"]):
                return CompatibilityResult(False, ("Train movement conflicts with protected block",), separate, coordinated, 0)
    reasons.extend(["Compatible block requirements", "No train conflict", "Shared block reduces downtime"])
    return CompatibilityResult(True, tuple(reasons), separate, coordinated, separate - coordinated)
