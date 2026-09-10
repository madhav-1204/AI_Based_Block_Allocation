"""Deterministic, relationship-aware synthetic railway planning data."""

from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from app.models.enums import AssetType, BlockType, Department, TaskStatus, TrafficDensity, TrainType

SEED = 42
BASE_DATE = date(2026, 9, 14)
HORIZON_DAYS = 30
CORRIDORS = {
    "C102": ("Secunderabad–Warangal", 110.0, 150.0),
    "C103": ("Delhi–Kanpur", 80.0, 125.0),
    "C104": ("Prayagraj–Varanasi", 40.0, 90.0),
}


def _iso_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def _priority_level(score: float) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _priority_score(criticality: float, safety: float, urgency: float, risk: float, availability: float) -> float:
    return round(0.30 * criticality + 0.25 * safety + 0.20 * urgency + 0.15 * risk + 0.10 * availability, 2)


def _urgency(days_until_due: int) -> float:
    if days_until_due < 0:
        return 100.0
    if days_until_due <= 2:
        return 90.0
    if days_until_due <= 7:
        return 75.0
    if days_until_due <= 14:
        return 60.0
    return 40.0


def _task_record(
    task_code: str,
    source_system: str,
    asset: dict[str, Any],
    department: Department,
    task_type: str,
    description: str,
    reported_at: datetime,
    due_at: datetime,
    duration: int,
    criticality: float,
    safety: float,
    risk: float,
    availability: float,
    block_type: BlockType,
    status: TaskStatus,
) -> dict[str, Any]:
    urgency = _urgency((due_at.date() - BASE_DATE).days)
    score = _priority_score(criticality, safety, urgency, risk, availability)
    return {
        "task_code": task_code,
        "source_system": source_system,
        "asset_code": asset["asset_code"],
        "department": department.value,
        "corridor_id": asset["corridor_id"],
        "location_start": asset["location_start"],
        "location_end": asset["location_end"],
        "task_type": task_type,
        "description": description,
        "reported_at": _iso_datetime(reported_at),
        "due_at": _iso_datetime(due_at),
        "estimated_duration_minutes": duration,
        "criticality": criticality,
        "safety_impact": safety,
        "urgency": urgency,
        "failure_risk": risk,
        "availability_impact": availability,
        "required_block_type": block_type.value,
        "required_resources": f"{department.value.lower()}_crew",
        "status": status.value,
        "priority_score": score,
        "priority_level": _priority_level(score),
    }


def generate_dataset(seed: int = SEED) -> dict[str, Any]:
    """Generate a reproducible dataset with intentional spatial and time relationships."""

    rng = random.Random(seed)
    assets: list[dict[str, Any]] = []
    asset_templates = [
        (AssetType.TRACK, Department.ENGINEERING, "Track panel"),
        (AssetType.SIGNAL, Department.SNT, "Signal equipment"),
        (AssetType.OHE, Department.TRACTION, "OHE equipment"),
        (AssetType.POINT_MACHINE, Department.SNT, "Point machine"),
    ]
    for index in range(360):
        corridor_id = list(CORRIDORS)[index % len(CORRIDORS)]
        _, low, high = CORRIDORS[corridor_id]
        asset_type, department, _ = asset_templates[index % len(asset_templates)]
        location = round(rng.uniform(low, high - 1), 1)
        health = round(rng.uniform(55, 99), 2)
        assets.append({
            "asset_code": f"{department.value[:3]}-{corridor_id}-{index + 1:04d}",
            "asset_type": asset_type.value,
            "department": department.value,
            "corridor_id": corridor_id,
            "location_start": location,
            "location_end": round(location + rng.uniform(0.2, 1.4), 1),
            "criticality": round(rng.uniform(45, 98), 2),
            "health_score": health,
            "installation_date": (BASE_DATE - timedelta(days=rng.randint(365, 3650))).isoformat(),
            "last_maintenance_date": (BASE_DATE - timedelta(days=rng.randint(5, 180))).isoformat(),
            "failure_count": rng.randint(0, 6),
            "operational_importance": round(rng.uniform(45, 100), 2),
        })

    # These three assets deliberately overlap at KM 120-124 on C102.
    overlap_assets = [
        ("ENG-C102-DEMO", AssetType.TRACK, Department.ENGINEERING, 120.0, 124.0),
        ("SNT-C102-DEMO", AssetType.SIGNAL, Department.SNT, 121.0, 123.5),
        ("TRC-C102-DEMO", AssetType.OHE, Department.TRACTION, 120.5, 123.0),
    ]
    for code, asset_type, department, start, end in overlap_assets:
        assets.append({
            "asset_code": code, "asset_type": asset_type.value, "department": department.value,
            "corridor_id": "C102", "location_start": start, "location_end": end,
            "criticality": 92.0, "health_score": 48.0, "installation_date": "2012-01-15",
            "last_maintenance_date": "2026-06-01", "failure_count": 3, "operational_importance": 96.0,
        })

    asset_by_code = {asset["asset_code"]: asset for asset in assets}
    tasks: list[dict[str, Any]] = []
    department_sources = {Department.ENGINEERING: "TMS", Department.SNT: "SMMS", Department.TRACTION: "TDMS"}
    task_types = {
        Department.ENGINEERING: ("rail inspection", BlockType.LINE_BLOCK),
        Department.SNT: ("signal maintenance", BlockType.TRAFFIC_BLOCK),
        Department.TRACTION: ("OHE maintenance", BlockType.POWER_BLOCK),
    }
    for index in range(1200):
        asset = assets[index % len(assets)]
        department = Department(asset["department"])
        task_type, block_type = task_types[department]
        reported_at = datetime.combine(BASE_DATE - timedelta(days=rng.randint(1, 45)), time(8), tzinfo=timezone.utc)
        due_at = datetime.combine(BASE_DATE + timedelta(days=rng.randint(-3, 25)), time(18), tzinfo=timezone.utc)
        status = TaskStatus.OVERDUE if due_at.date() < BASE_DATE else TaskStatus.PENDING
        tasks.append(_task_record(
            f"{department.value[:3]}-{index + 1:05d}", department_sources[department], asset, department,
            task_type, f"Synthetic {task_type} for {asset['asset_code']}", reported_at, due_at,
            rng.choice([45, 60, 90, 120]), round(rng.uniform(45, 98), 2), round(rng.uniform(40, 99), 2),
            round(rng.uniform(35, 96), 2), round(rng.uniform(40, 98), 2), block_type, status,
        ))

    demo_specs = [
        ("ENG-C102-DEMO", Department.ENGINEERING, "track inspection", 90, BlockType.LINE_BLOCK),
        ("SNT-C102-DEMO", Department.SNT, "signal maintenance", 45, BlockType.TRAFFIC_BLOCK),
        ("TRC-C102-DEMO", Department.TRACTION, "OHE maintenance", 60, BlockType.POWER_BLOCK),
    ]
    for offset, (asset_code, department, task_type, duration, block_type) in enumerate(demo_specs):
        asset = asset_by_code[asset_code]
        reported = datetime.combine(BASE_DATE - timedelta(days=2), time(7 + offset), tzinfo=timezone.utc)
        due = datetime.combine(BASE_DATE + timedelta(days=2), time(18), tzinfo=timezone.utc)
        tasks.append(_task_record(
            f"{department.value[:3]}-C102-DEMO", department_sources[department], asset, department,
            task_type, f"Coordinated C102 demo task: {task_type}", reported, due, duration,
            94.0, 95.0, 90.0, 92.0, block_type, TaskStatus.PENDING,
        ))

    trains: list[dict[str, Any]] = []
    train_types = list(TrainType)
    for day_offset in range(HORIZON_DAYS):
        current_date = BASE_DATE + timedelta(days=day_offset)
        for corridor_index, corridor_id in enumerate(CORRIDORS):
            for movement in range(30):
                start_minutes = (movement * 47 + corridor_index * 13) % (24 * 60 - 20)
                start = datetime.combine(current_date, time.min, tzinfo=timezone.utc) + timedelta(minutes=start_minutes)
                trains.append({
                    "train_number": f"{12000 + corridor_index * 1000 + movement:05d}",
                    "train_type": train_types[(movement + corridor_index) % len(train_types)].value,
                    "corridor_id": corridor_id,
                    "start_time": _iso_datetime(start),
                    "end_time": _iso_datetime(start + timedelta(minutes=rng.choice([5, 10, 15, 20]))),
                    "priority": 3 if movement % 7 == 0 else 1,
                    "traffic_category": "HIGH" if movement % 3 == 0 else "MEDIUM",
                })

    block_windows: list[dict[str, Any]] = []
    for day_offset in range(HORIZON_DAYS):
        current_date = BASE_DATE + timedelta(days=day_offset)
        for corridor_id in CORRIDORS:
            for start_hour, block_type in [(1, BlockType.COMBINED_BLOCK), (10, BlockType.LINE_BLOCK), (14, BlockType.POWER_BLOCK), (22, BlockType.TRAFFIC_BLOCK)]:
                block_windows.append({
                    "corridor_id": corridor_id, "date": current_date.isoformat(),
                    "start_time": f"{start_hour:02d}:00:00", "end_time": f"{start_hour + 2:02d}:00:00",
                    "block_type": block_type.value, "available": True, "maximum_duration_minutes": 120,
                })

    goods_forecasts: list[dict[str, Any]] = []
    for day_offset in range(HORIZON_DAYS):
        current_date = BASE_DATE + timedelta(days=day_offset)
        for corridor_index, corridor_id in enumerate(CORRIDORS):
            for start_hour in [0, 6, 12, 18]:
                expected = 1 + ((day_offset + corridor_index + start_hour) % 5)
                goods_forecasts.append({
                    "corridor_id": corridor_id, "date": current_date.isoformat(),
                    "time_window_start": f"{start_hour:02d}:00:00", "time_window_end": f"{(start_hour + 6) % 24:02d}:00:00",
                    "expected_goods_trains": expected,
                    "traffic_density": TrafficDensity.LOW.value if expected <= 2 else TrafficDensity.MEDIUM.value if expected <= 4 else TrafficDensity.HIGH.value,
                })

    resources = [
        {"resource_code": "ENG-CREW-01", "department": Department.ENGINEERING.value, "resource_type": "Track maintenance crew", "capacity": 3},
        {"resource_code": "ENG-ULTRA-01", "department": Department.ENGINEERING.value, "resource_type": "Ultrasonic inspection unit", "capacity": 1},
        {"resource_code": "SNT-CREW-01", "department": Department.SNT.value, "resource_type": "Signal maintenance crew", "capacity": 2},
        {"resource_code": "SNT-TEST-01", "department": Department.SNT.value, "resource_type": "Axle counter tester", "capacity": 1},
        {"resource_code": "TRC-CREW-01", "department": Department.TRACTION.value, "resource_type": "OHE maintenance crew", "capacity": 2},
        {"resource_code": "TRC-TOWER-01", "department": Department.TRACTION.value, "resource_type": "Tower wagon", "capacity": 1},
    ]
    return {
        "metadata": {"seed": seed, "generated_at": _iso_datetime(datetime.now(timezone.utc)), "synthetic": True, "base_date": BASE_DATE.isoformat()},
        "assets": assets, "maintenance_tasks": tasks, "trains": trains,
        "block_windows": block_windows, "goods_forecasts": goods_forecasts, "resources": resources,
    }
