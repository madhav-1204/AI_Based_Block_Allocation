from sqlalchemy import inspect, text

from app.db.database import engine


def test_core_schema_is_available() -> None:
    inspector = inspect(engine)
    expected_tables = {
        "assets",
        "block_plan_tasks",
        "block_plans",
        "block_windows",
        "goods_forecasts",
        "maintenance_tasks",
        "resources",
        "trains",
    }

    assert expected_tables.issubset(set(inspector.get_table_names()))
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
