from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_data_endpoints() -> None:
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/assets?corridor=C102").status_code == 200
    tasks = client.get("/api/tasks?corridor=C102&limit=5")
    assert tasks.status_code == 200
    assert len(tasks.json()["items"]) == 5
    assert client.get("/api/trains?corridor=C102&limit=5").status_code == 200
    assert client.get("/api/blocks?corridor=C102&limit=5").status_code == 200


def test_optimize_and_analytics_endpoints() -> None:
    plan = client.post("/api/optimize", json={"planning_horizon": "WEEKLY"})
    assert plan.status_code == 200
    assert plan.json()["planning_horizon"] == "WEEKLY"
    analytics = client.get("/api/analytics")
    assert analytics.status_code == 200
    assert "before" in analytics.json()
    assert "after" in analytics.json()


def test_emergency_endpoint_validates_input() -> None:
    response = client.post("/api/simulation/emergency", json={"corridor_id": "C102", "location_start": 120, "location_end": 121, "department": "ENGINEERING"})
    assert response.status_code == 200
    assert response.json()["emergency_task"]["status"] == "EMERGENCY"
