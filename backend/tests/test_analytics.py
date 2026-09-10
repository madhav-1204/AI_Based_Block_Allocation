from app.services.analytics import calculate_analytics
from app.services.optimization.optimizer import Optimizer


def task(task_id: str, department: str, required_block_type: str, duration: int, score: float) -> dict:
    return {"task_id": task_id, "department": department, "corridor_id": "C102", "location_start": 120.0, "location_end": 124.0, "estimated_duration_minutes": duration, "required_block_type": required_block_type, "priority_score": score, "due_at": "2026-09-20T18:00:00+00:00", "status": "PENDING", "asset_health_score": 70}


def test_analytics_calculates_actual_shared_block_improvement() -> None:
    tasks = [task("ENG-1", "ENGINEERING", "LINE_BLOCK", 90, 94), task("SNT-1", "SNT", "TRAFFIC_BLOCK", 45, 92), task("TRA-1", "TRACTION", "POWER_BLOCK", 60, 91)]
    blocks = [{"corridor_id": "C102", "date": "2026-09-14", "start_time": "01:00:00", "end_time": "03:00:00", "block_type": "COMBINED_BLOCK", "available": True}]
    plan = Optimizer().optimize(tasks, [], blocks)
    result = calculate_analytics(tasks, blocks, plan)
    assert result["before"]["downtime_minutes"] == 195
    assert result["after"]["downtime_minutes"] == 90
    assert result["improvement"]["downtime_reduced_percent"] == round((195 - 90) / 195 * 100, 2)
    assert result["after"]["blocks"] == 1
