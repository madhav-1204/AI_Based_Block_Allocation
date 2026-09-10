from app.services.planning import EmergencyReplanner, PlanningService


def task(task_id: str, department: str, required_block_type: str, duration: int, score: float) -> dict:
    return {"task_id": task_id, "department": department, "corridor_id": "C102", "location_start": 120.0, "location_end": 124.0, "estimated_duration_minutes": duration, "required_block_type": required_block_type, "priority_score": score, "due_at": "2026-09-20T18:00:00+00:00", "status": "PENDING"}


def blocks() -> list[dict]:
    return [{"corridor_id": "C102", "date": "2026-09-14", "start_time": "01:00:00", "end_time": "03:00:00", "block_type": "COMBINED_BLOCK", "available": True}]


def test_planning_service_returns_contract_summary() -> None:
    plan = PlanningService().generate_plan([task("ENG-1", "ENGINEERING", "LINE_BLOCK", 90, 94)], [], blocks())
    summary = PlanningService.plan_summary(plan)
    assert summary["status"] in {"OPTIMAL", "FEASIBLE"}
    assert summary["blocks"][0]["tasks"][0]["task_id"] == "ENG-1"


def test_emergency_replanner_marks_critical_and_preserves_completed() -> None:
    result = EmergencyReplanner().replan({"task_id": "EMG-1", "corridor_id": "C102", "location_start": 120.0, "location_end": 124.0, "department": "ENGINEERING"}, [task("DONE-1", "ENGINEERING", "LINE_BLOCK", 90, 94)], [], blocks(), completed_task_ids={"DONE-1"})
    assert result.emergency_task["status"] == "EMERGENCY"
    assert result.emergency_task["priority_level"] == "CRITICAL"
    assert "Completed tasks were preserved." in result.explanation
