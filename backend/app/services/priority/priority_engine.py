from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class PriorityResult:
    score: float
    level: str
    components: dict[str, float]


class PriorityEngine:
    """Transparent weighted priority scoring for maintenance tasks."""

    weights = {
        "criticality": 0.30,
        "safety_impact": 0.25,
        "urgency": 0.20,
        "failure_risk": 0.15,
        "availability_impact": 0.10,
    }

    def calculate(self, task: dict, today: date | None = None) -> PriorityResult:
        today = today or date.today()
        components = {name: max(0.0, min(100.0, float(task.get(name, 0)))) for name in self.weights}
        due_at = task.get("due_at")
        is_emergency = task.get("status") == "EMERGENCY"
        if is_emergency:
            components["urgency"] = 100.0
        elif due_at:
            due_date = due_at.date() if hasattr(due_at, "date") else date.fromisoformat(str(due_at)[:10])
            days = (due_date - today).days
            components["urgency"] = 100.0 if days < 0 else 90.0 if days <= 2 else 75.0 if days <= 7 else 60.0 if days <= 14 else 40.0
        score = round(sum(components[name] * weight for name, weight in self.weights.items()), 2)
        if is_emergency:
            score = max(score, 90.0)
        level = "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 40 else "LOW"
        return PriorityResult(score, level, components)
