from app.services.optimization.optimizer import Optimizer


def task(task_id: str, department: str, required_block_type: str, duration: int, score: float) -> dict:
    return {"task_id": task_id, "department": department, "corridor_id": "C102", "location_start": 120.0, "location_end": 124.0, "estimated_duration_minutes": duration, "required_block_type": required_block_type, "priority_score": score, "due_at": "2026-09-20T18:00:00+00:00", "status": "PENDING"}


def block(block_type: str = "COMBINED_BLOCK") -> dict:
    return {"corridor_id": "C102", "date": "2026-09-14", "start_time": "01:00:00", "end_time": "03:00:00", "block_type": block_type, "available": True}


def test_optimizer_groups_c102_tasks_and_calculates_savings() -> None:
    plan = Optimizer().optimize([task("ENG-C102-DEMO", "ENGINEERING", "LINE_BLOCK", 90, 94), task("SNT-C102-DEMO", "SNT", "TRAFFIC_BLOCK", 45, 92), task("TRA-C102-DEMO", "TRACTION", "POWER_BLOCK", 60, 91)], [], [block()])
    assert plan.status in {"OPTIMAL", "FEASIBLE"}
    assert len(plan.blocks) == 1
    assert plan.blocks[0].shared_block
    assert plan.blocks[0].shared_block_savings_minutes == 105
    assert len(plan.assigned_task_ids) == 3


def test_optimizer_rejects_train_conflict() -> None:
    trains = [{"train_number": "12723", "corridor_id": "C102", "start_time": "2026-09-14T01:30:00+00:00", "end_time": "2026-09-14T01:35:00+00:00"}]
    plan = Optimizer().optimize([task("ENG-1", "ENGINEERING", "LINE_BLOCK", 60, 90)], trains, [block()])
    assert plan.status == "INFEASIBLE"
