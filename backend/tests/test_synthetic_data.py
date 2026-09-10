from collections import Counter

from app.services.synthetic_data import generate_dataset


def test_generation_is_deterministic_and_relationship_aware() -> None:
    first = generate_dataset()
    second = generate_dataset()

    assert first["assets"] == second["assets"]
    assert first["maintenance_tasks"] == second["maintenance_tasks"]
    assert len(first["assets"]) == 363
    assert len(first["maintenance_tasks"]) == 1203
    assert len(first["trains"]) == 2700
    assert len(first["block_windows"]) == 360
    assert len(first["goods_forecasts"]) == 360
    assert sum(Counter(task["source_system"] for task in first["maintenance_tasks"]).values()) == 1203


def test_c102_demo_tasks_overlap_across_departments() -> None:
    dataset = generate_dataset()
    demo_tasks = [task for task in dataset["maintenance_tasks"] if task["task_code"].endswith("C102-DEMO")]

    assert {task["department"] for task in demo_tasks} == {"ENGINEERING", "SNT", "TRACTION"}
    assert {task["corridor_id"] for task in demo_tasks} == {"C102"}
    assert max(task["location_start"] for task in demo_tasks) < min(task["location_end"] for task in demo_tasks)
    assert sum(task["estimated_duration_minutes"] for task in demo_tasks) == 195
