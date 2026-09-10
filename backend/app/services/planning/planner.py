from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.services.optimization.optimizer import OptimizedPlan, Optimizer


@dataclass(frozen=True)
class PlanningRequest:
    planning_horizon: str = "WEEKLY"
    objective: str = "MAXIMIZE_ASSET_AVAILABILITY"


class PlanningService:
    """Application service that owns the planning workflow around the optimizer."""

    def __init__(self, optimizer: Optimizer | None = None) -> None:
        self.optimizer = optimizer or Optimizer()

    def generate_plan(self, tasks: list[dict], trains: list[dict], blocks: list[dict], goods_forecasts: list[dict] | None = None, resources: list[dict] | None = None, request: PlanningRequest | None = None) -> OptimizedPlan:
        request = request or PlanningRequest()
        return self.optimizer.optimize(tasks, trains, blocks, goods_forecasts, resources, request.planning_horizon)

    @staticmethod
    def plan_summary(plan: OptimizedPlan) -> dict:
        return {
            "status": plan.status,
            "planning_horizon": plan.planning_horizon,
            "generated_at": datetime.now().astimezone().isoformat(),
            "blocks": [
                {
                    "block_id": block.block_id,
                    "corridor_id": block.corridor_id,
                    "date": block.date.isoformat(),
                    "start_time": block.start_time.isoformat(),
                    "end_time": block.end_time.isoformat(),
                    "block_type": block.block_type,
                    "departments": sorted({task.department for task in block.tasks}),
                    "tasks": [{"task_id": task.task_id, "department": task.department, "priority_score": task.priority_score} for task in block.tasks],
                    "utilization": block.utilization,
                    "shared_block": block.shared_block,
                    "shared_block_savings_minutes": block.shared_block_savings_minutes,
                    "optimization_score": block.optimization_score,
                    "reason": list(block.reasons),
                }
                for block in plan.blocks
            ],
        }
