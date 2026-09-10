from datetime import date

from app.services.priority import PriorityEngine
from app.services.risk import RiskModel


def test_priority_uses_configured_weights_and_due_date() -> None:
    result = PriorityEngine().calculate({"criticality": 100, "safety_impact": 100, "urgency": 0, "failure_risk": 100, "availability_impact": 100, "due_at": "2026-09-14T18:00:00+00:00"}, today=date(2026, 9, 10))
    assert result.components["urgency"] == 75
    assert result.score == 95.0
    assert result.level == "CRITICAL"


def test_emergency_is_always_urgent() -> None:
    result = PriorityEngine().calculate({"status": "EMERGENCY", "criticality": 70, "safety_impact": 70, "failure_risk": 70, "availability_impact": 70}, today=date(2026, 9, 10))
    assert result.components["urgency"] == 100
    assert result.level == "CRITICAL"


def test_risk_increases_for_unhealthy_repeatedly_failed_assets() -> None:
    model = RiskModel()
    healthy = model.predict({"health_score": 95, "criticality": 40, "failure_count": 0, "operational_importance": 40})
    risky = model.predict({"health_score": 35, "criticality": 95, "failure_count": 5, "operational_importance": 95})
    assert healthy.method == "deterministic_fallback"
    assert risky.score > healthy.score
    assert 0 <= risky.probability <= 1
