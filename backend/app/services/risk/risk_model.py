from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    probability: float
    score: float
    method: str


class RiskModel:
    """Deterministic fallback risk model; replaceable by a trained classifier later."""

    def predict(self, asset: dict, task: dict | None = None) -> RiskResult:
        health = max(0.0, min(100.0, float(asset.get("health_score", 100))))
        criticality = max(0.0, min(100.0, float(asset.get("criticality", 0))))
        failures = min(100.0, float(asset.get("failure_count", 0)) * 12.5)
        importance = max(0.0, min(100.0, float(asset.get("operational_importance", 0))))
        task_risk = max(0.0, min(100.0, float((task or {}).get("failure_risk", 0))))
        score = round(0.35 * (100 - health) + 0.25 * criticality + 0.15 * failures + 0.15 * importance + 0.10 * task_risk, 2)
        return RiskResult(round(score / 100, 4), score, "deterministic_fallback")
