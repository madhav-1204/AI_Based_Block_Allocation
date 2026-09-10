from datetime import datetime, timezone

from app.services.optimization.compatibility import check_compatibility


def task(department: str, start: float, end: float, duration: int, block_type: str = "COMBINED_BLOCK") -> dict:
    return {"department": department, "corridor_id": "C102", "location_start": start, "location_end": end, "estimated_duration_minutes": duration, "required_block_type": block_type, "required_resources": f"{department.lower()}_crew"}


def test_c102_tasks_can_share_and_save_105_minutes() -> None:
    result = check_compatibility([task("ENGINEERING", 120, 124, 90), task("SNT", 121, 123.5, 45), task("TRACTION", 120.5, 123, 60)], block_type="COMBINED_BLOCK", max_duration_minutes=120, resources_available={"engineering_crew", "snt_crew", "traction_crew"})
    assert result.compatible
    assert result.separate_duration_minutes == 195
    assert result.coordinated_duration_minutes == 90
    assert result.savings_minutes == 105


def test_different_corridors_are_rejected() -> None:
    first = task("ENGINEERING", 120, 124, 90)
    second = {**task("SNT", 121, 123, 45), "corridor_id": "C103"}
    result = check_compatibility([first, second], block_type="COMBINED_BLOCK", max_duration_minutes=120)
    assert not result.compatible


def test_train_overlap_is_a_hard_rejection() -> None:
    result = check_compatibility([task("ENGINEERING", 120, 124, 90)], block_type="COMBINED_BLOCK", max_duration_minutes=120, block_start=datetime(2026, 9, 14, 10, tzinfo=timezone.utc), block_end=datetime(2026, 9, 14, 11, 30, tzinfo=timezone.utc), conflicting_trains=[{"corridor_id": "C102", "start_time": datetime(2026, 9, 14, 10, 20, tzinfo=timezone.utc), "end_time": datetime(2026, 9, 14, 10, 25, tzinfo=timezone.utc)}])
    assert not result.compatible
    assert "Train movement conflicts" in result.reasons[0]
