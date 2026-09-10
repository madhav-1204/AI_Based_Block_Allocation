from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

from ortools.sat.python import cp_model

from app.services.optimization.train_conflicts import is_block_safe


@dataclass(frozen=True)
class OptimizedTask:
    task_id: str
    priority_score: float
    department: str


@dataclass(frozen=True)
class OptimizedBlock:
    block_id: str
    corridor_id: str
    date: date
    start_time: time
    end_time: time
    block_type: str
    tasks: tuple[OptimizedTask, ...]
    utilization: float
    shared_block: bool
    shared_block_savings_minutes: int
    optimization_score: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class OptimizedPlan:
    status: str
    planning_horizon: str
    blocks: tuple[OptimizedBlock, ...]
    assigned_task_ids: tuple[str, ...]


class Optimizer:
    """CP-SAT maintenance assignment optimizer for feasible block candidates."""

    def __init__(self, time_limit_seconds: float = 5.0) -> None:
        self.time_limit_seconds = time_limit_seconds

    def optimize(self, tasks: list[dict], trains: list[dict], blocks: list[dict], goods_forecast: list[dict] | None = None, resources: list[dict] | None = None, planning_horizon: str = "WEEKLY") -> OptimizedPlan:
        model = cp_model.CpModel()
        trains_by_corridor_date: dict[tuple[str, str], list[dict]] = {}
        for train in trains:
            normalized_train = self._normalize_train(train)
            trains_by_corridor_date.setdefault((normalized_train["corridor_id"], normalized_train["start_time"].date().isoformat()), []).append(normalized_train)
        candidates: list[tuple[int, int]] = []
        for task_index, task in enumerate(tasks):
            for block_index, block in enumerate(blocks):
                candidate_trains = trains_by_corridor_date.get((block["corridor_id"], block["date"]), [])
                if self._is_feasible(task, block, candidate_trains):
                    candidates.append((task_index, block_index))
        if not candidates:
            return OptimizedPlan("INFEASIBLE", planning_horizon, (), ())

        assignments = {candidate: model.new_bool_var(f"task_{candidate[0]}_block_{candidate[1]}") for candidate in candidates}
        used_blocks = {block_index: model.new_bool_var(f"block_{block_index}") for _, block_index in candidates}
        for task_index in range(len(tasks)):
            task_vars = [variable for (candidate_task, _), variable in assignments.items() if candidate_task == task_index]
            if task_vars:
                model.add(sum(task_vars) <= 1)
        for block_index, used in used_blocks.items():
            block_vars = [variable for (candidate_task, candidate_block), variable in assignments.items() if candidate_block == block_index]
            model.add_max_equality(used, block_vars)
        objective_terms = []
        for (task_index, block_index), variable in assignments.items():
            priority = int(round(float(tasks[task_index].get("priority_score", 0)) * 100))
            objective_terms.append(variable * (priority + 100))
        model.maximize(sum(objective_terms) - sum(used_blocks.values()) * 10)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        solver.parameters.num_search_workers = 1
        result = solver.solve(model)
        if result not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return OptimizedPlan("INFEASIBLE", planning_horizon, (), ())

        selected: dict[int, list[int]] = {}
        for (task_index, block_index), variable in assignments.items():
            if solver.value(variable):
                selected.setdefault(block_index, []).append(task_index)
        optimized_blocks = tuple(self._build_block(blocks[index], [tasks[task_index] for task_index in task_indexes], index) for index, task_indexes in selected.items())
        assigned = tuple(task.task_id for block in optimized_blocks for task in block.tasks)
        status = "OPTIMAL" if result == cp_model.OPTIMAL else "FEASIBLE"
        return OptimizedPlan(status, planning_horizon, optimized_blocks, assigned)

    @staticmethod
    def _is_feasible(task: dict, block: dict, trains: list[dict]) -> bool:
        if task["corridor_id"] != block["corridor_id"] or not block.get("available", True):
            return False
        if task.get("required_block_type") not in {block["block_type"], "COMBINED_BLOCK"} and block["block_type"] != "COMBINED_BLOCK":
            return False
        duration = int(task["estimated_duration_minutes"])
        start = datetime.combine(date.fromisoformat(block["date"]), time.fromisoformat(block["start_time"]), tzinfo=UTC)
        end = datetime.combine(date.fromisoformat(block["date"]), time.fromisoformat(block["end_time"]), tzinfo=UTC)
        if duration > (end - start).total_seconds() / 60:
            return False
        due_at = task.get("due_at")
        if due_at and date.fromisoformat(str(due_at)[:10]) < start.date() and task.get("status") != "OVERDUE":
            return False
        return is_block_safe(block["corridor_id"], start, end, trains)

    @staticmethod
    def _normalize_train(train: dict) -> dict:
        result = {**train}
        if isinstance(result["start_time"], str):
            result["start_time"] = datetime.fromisoformat(result["start_time"])
        if isinstance(result["end_time"], str):
            result["end_time"] = datetime.fromisoformat(result["end_time"])
        return result

    @staticmethod
    def _build_block(block: dict, tasks: list[dict], block_index: int) -> OptimizedBlock:
        durations = [int(task["estimated_duration_minutes"]) for task in tasks]
        duration = max(durations)
        start = time.fromisoformat(block["start_time"])
        end = (datetime.combine(date.today(), start) + timedelta(minutes=duration)).time()
        max_duration = (datetime.combine(date.today(), time.fromisoformat(block["end_time"])) - datetime.combine(date.today(), start)).total_seconds() / 60
        optimized_tasks = tuple(OptimizedTask(str(task["task_id"]), float(task.get("priority_score", 0)), str(task["department"])) for task in tasks)
        return OptimizedBlock(f"B-{block_index + 1:03d}", block["corridor_id"], date.fromisoformat(block["date"]), start, end, block["block_type"], optimized_tasks, round(duration / max_duration, 3), len(tasks) > 1, sum(durations) - duration, round(sum(task.get("priority_score", 0) for task in tasks) / len(tasks), 2), ("High priority maintenance", "No train conflict", "Shared block reduces downtime"))
