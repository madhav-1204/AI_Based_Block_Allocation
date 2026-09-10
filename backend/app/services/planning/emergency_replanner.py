from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.services.planning.planner import PlanningRequest, PlanningService


@dataclass(frozen=True)
class EmergencyReplanResult:
    emergency_task: dict
    old_plan: object
    new_plan: object
    changed_task_ids: tuple[str, ...]
    explanation: tuple[str, ...]


class EmergencyReplanner:
    """Replan safely around an emergency while retaining completed task assignments."""

    def __init__(self, planning_service: PlanningService | None = None) -> None:
        self.planning_service = planning_service or PlanningService()

    def replan(self, emergency: dict, tasks: list[dict], trains: list[dict], blocks: list[dict], completed_task_ids: set[str] | None = None) -> EmergencyReplanResult:
        completed_task_ids = completed_task_ids or set()
        emergency_task = {**emergency, "task_id": emergency.get("task_id", "EMERGENCY-001"), "status": "EMERGENCY", "priority_score": 100.0, "priority_level": "CRITICAL", "required_block_type": emergency.get("required_block_type", "COMBINED_BLOCK"), "estimated_duration_minutes": emergency.get("estimated_duration_minutes", 60)}
        eligible_tasks = [task for task in tasks if task.get("task_id") not in completed_task_ids]
        old_plan = self.planning_service.generate_plan(eligible_tasks, trains, blocks, request=PlanningRequest())
        new_plan = self.planning_service.generate_plan([*eligible_tasks, emergency_task], trains, blocks, request=PlanningRequest())
        old_ids = set(old_plan.assigned_task_ids)
        new_ids = set(new_plan.assigned_task_ids)
        changed = tuple(sorted((old_ids ^ new_ids) | ({emergency_task["task_id"]} if emergency_task["task_id"] in new_ids else set())))
        explanation = (f"Emergency defect detected on {emergency_task['corridor_id']}.", "Emergency task classified as CRITICAL.", "Completed tasks were preserved.", "Train conflicts remained hard constraints.")
        return EmergencyReplanResult(emergency_task, old_plan, new_plan, changed, explanation)
