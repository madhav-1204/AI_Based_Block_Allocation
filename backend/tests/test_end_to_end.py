from fastapi.testclient import TestClient

from app.main import app


def test_sih_demo_flow_from_data_to_emergency_replan() -> None:
    client = TestClient(app)

    assert client.get("/api/health").json()["status"] == "healthy"
    task_response = client.get("/api/tasks?corridor=C102&limit=10")
    assert task_response.status_code == 200
    assert task_response.json()["items"]

    plan_response = client.post("/api/optimize", json={"planning_horizon": "WEEKLY", "objective": "MAXIMIZE_ASSET_AVAILABILITY"})
    assert plan_response.status_code == 200
    plan = plan_response.json()
    assert plan["planning_horizon"] == "WEEKLY"
    assert plan["status"] in {"OPTIMAL", "FEASIBLE", "INFEASIBLE"}

    analytics_response = client.get("/api/analytics")
    assert analytics_response.status_code == 200
    assert analytics_response.json()["before"]["blocks"] > 0

    emergency_response = client.post("/api/simulation/emergency", json={"task_id": "EMG-E2E-001", "corridor_id": "C102", "location_start": 120, "location_end": 121, "department": "ENGINEERING", "description": "Synthetic critical defect"})
    assert emergency_response.status_code == 200
    emergency = emergency_response.json()
    assert emergency["emergency_task"]["status"] == "EMERGENCY"
    assert emergency["new_plan"]["status"] in {"OPTIMAL", "FEASIBLE", "INFEASIBLE"}
    assert emergency["explanation"]
