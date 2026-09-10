from __future__ import annotations

from typing import Any

from app.services.optimization.optimizer import OptimizedPlan


def _availability(tasks: list[dict[str, Any]], downtime_minutes: int) -> float:
    """Prototype metric, not an official railway availability calculation."""

    if not tasks:
        return 1.0
    health = sum(float(task.get("asset_health_score", 85.0)) for task in tasks) / len(tasks) / 100
    overdue = sum(task.get("status") == "OVERDUE" for task in tasks)
    overdue_ratio = overdue / len(tasks)
    downtime_penalty = min(0.15, downtime_minutes / max(1, len(tasks) * 24 * 60) * 0.15)
    return round(max(0.0, min(1.0, health - overdue_ratio * 0.08 - downtime_penalty)), 4)


def _snapshot(tasks: list[dict[str, Any]], block_count: int, downtime: int, utilization: float) -> dict[str, Any]:
    return {"blocks": block_count, "downtime_minutes": downtime, "utilization": round(utilization, 4), "asset_availability": _availability(tasks, downtime), "overdue_tasks": sum(task.get("status") == "OVERDUE" for task in tasks), "tasks_completed": len(tasks)}


def calculate_analytics(tasks: list[dict[str, Any]], available_blocks: list[dict[str, Any]], plan: OptimizedPlan) -> dict[str, Any]:
    """Calculate actual before/after planning metrics from supplied records."""

    before_downtime = sum(int(task.get("estimated_duration_minutes", 0)) for task in tasks)
    before_capacity = sum(_block_capacity(block) for block in available_blocks)
    after_downtime = sum(max((int(task.get("estimated_duration_minutes", 0)) for task in _task_inputs(plan, tasks, block)), default=0) for block in plan.blocks)
    after_capacity = sum(_block_capacity(block) for block in available_blocks) or 1
    before = _snapshot(tasks, len(available_blocks), before_downtime, before_downtime / max(1, before_capacity))
    after_tasks = [task for task in tasks if task.get("task_id") in plan.assigned_task_ids]
    after = _snapshot(after_tasks, len(plan.blocks), after_downtime, after_downtime / after_capacity)
    return {"before": before, "after": after, "improvement": {"blocks_reduced_percent": _improvement(before["blocks"], after["blocks"]), "downtime_reduced_percent": _improvement(before["downtime_minutes"], after["downtime_minutes"]), "availability_improvement_percent": round((after["asset_availability"] - before["asset_availability"]) * 100, 2)}}


def _block_capacity(block: dict[str, Any]) -> int:
    from datetime import datetime
    start = datetime.fromisoformat(f"2000-01-01T{block['start_time']}")
    end = datetime.fromisoformat(f"2000-01-01T{block['end_time']}")
    return max(0, int((end - start).total_seconds() / 60))


def _task_inputs(plan: OptimizedPlan, tasks: list[dict[str, Any]], block: Any) -> list[dict[str, Any]]:
    ids = {task.task_id for task in block.tasks}
    return [task for task in tasks if task.get("task_id") in ids]


def _improvement(before: int, after: int) -> float:
    return round((before - after) / before * 100, 2) if before else 0.0
