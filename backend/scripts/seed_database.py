from __future__ import annotations

import argparse
from datetime import date, datetime, time
from pathlib import Path
import sys

from sqlalchemy import delete
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import SessionLocal
from app.models import Asset, BlockPlan, BlockPlanTask, BlockWindow, GoodsForecast, MaintenanceTask, Resource, Train
from app.models.enums import AssetType, BlockPlanStatus, BlockType, Department, TaskStatus, TrafficDensity, TrainType
from app.services.synthetic_data import generate_dataset


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def seed_database(session: Session, seed: int = 42) -> dict[str, int]:
    dataset = generate_dataset(seed)
    session.execute(delete(BlockPlanTask))
    session.execute(delete(BlockPlan))
    session.execute(delete(MaintenanceTask))
    session.execute(delete(Train))
    session.execute(delete(BlockWindow))
    session.execute(delete(GoodsForecast))
    session.execute(delete(Resource))
    session.execute(delete(Asset))

    assets = [Asset(**{**record, "asset_type": AssetType(record["asset_type"]), "department": Department(record["department"]), "installation_date": date.fromisoformat(record["installation_date"]), "last_maintenance_date": date.fromisoformat(record["last_maintenance_date"])}) for record in dataset["assets"]]
    session.add_all(assets)
    session.flush()
    asset_ids = {asset.asset_code: asset.id for asset in assets}

    tasks = []
    for record in dataset["maintenance_tasks"]:
        task_data = {**record}
        task_data["asset_id"] = asset_ids[task_data.pop("asset_code")]
        task_data["department"] = Department(task_data["department"])
        task_data["required_block_type"] = BlockType(task_data["required_block_type"])
        task_data["status"] = TaskStatus(task_data["status"])
        task_data["reported_at"] = parse_datetime(task_data["reported_at"])
        task_data["due_at"] = parse_datetime(task_data["due_at"])
        tasks.append(MaintenanceTask(**task_data))
    session.add_all(tasks)

    session.add_all([Train(**{**record, "train_type": TrainType(record["train_type"]), "start_time": parse_datetime(record["start_time"]), "end_time": parse_datetime(record["end_time"])}) for record in dataset["trains"]])
    session.add_all([BlockWindow(**{**record, "date": date.fromisoformat(record["date"]), "start_time": time.fromisoformat(record["start_time"]), "end_time": time.fromisoformat(record["end_time"]), "block_type": BlockType(record["block_type"])}) for record in dataset["block_windows"]])
    session.add_all([GoodsForecast(**{**record, "date": date.fromisoformat(record["date"]), "time_window_start": time.fromisoformat(record["time_window_start"]), "time_window_end": time.fromisoformat(record["time_window_end"]), "traffic_density": TrafficDensity(record["traffic_density"])}) for record in dataset["goods_forecasts"]])
    session.add_all([Resource(**{**record, "department": Department(record["department"])}) for record in dataset["resources"]])
    session.commit()
    return {name: len(dataset[name]) for name in ("assets", "maintenance_tasks", "trains", "block_windows", "goods_forecasts", "resources")}


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed PostgreSQL with deterministic synthetic RailOpt AI data.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    with SessionLocal() as session:
        counts = seed_database(session, args.seed)
    print("Seeded synthetic database:")
    for name, count in counts.items():
        print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
