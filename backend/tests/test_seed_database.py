from sqlalchemy import func, select

from app.db.database import SessionLocal
from app.models import Asset, BlockWindow, GoodsForecast, MaintenanceTask, Resource, Train
from scripts.seed_database import seed_database


def test_seed_database_persists_expected_counts() -> None:
    with SessionLocal() as session:
        counts = seed_database(session, seed=42)
        persisted = {
            "assets": session.scalar(select(func.count()).select_from(Asset)),
            "maintenance_tasks": session.scalar(select(func.count()).select_from(MaintenanceTask)),
            "trains": session.scalar(select(func.count()).select_from(Train)),
            "block_windows": session.scalar(select(func.count()).select_from(BlockWindow)),
            "goods_forecasts": session.scalar(select(func.count()).select_from(GoodsForecast)),
            "resources": session.scalar(select(func.count()).select_from(Resource)),
        }

    assert persisted == counts
    assert persisted == {
        "assets": 363,
        "maintenance_tasks": 1203,
        "trains": 2700,
        "block_windows": 360,
        "goods_forecasts": 360,
        "resources": 6,
    }
