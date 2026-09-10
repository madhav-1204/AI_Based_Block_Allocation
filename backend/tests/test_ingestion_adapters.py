from pathlib import Path

from app.services.ingestion import COAAdapter, GoodsForecastAdapter, SMMSAdapter, TDMSAdapter, TMSAdapter, TimetableAdapter

DATASET = Path(__file__).parents[2] / "data" / "synthetic" / "synthetic_dataset.json"


def test_source_adapters_normalize_synthetic_sources() -> None:
    assert len(TMSAdapter(DATASET).load()) == 302
    assert len(SMMSAdapter(DATASET).load()) == 599
    assert len(TDMSAdapter(DATASET).load()) == 302
    assert len(COAAdapter(DATASET).load()) == 360
    assert len(TimetableAdapter(DATASET).load()) == 2700
    assert len(GoodsForecastAdapter(DATASET).load()) == 360


def test_adapters_preserve_c102_cross_source_relationships() -> None:
    engineering = [item for item in TMSAdapter(DATASET).load() if item["task_code"] == "ENG-C102-DEMO"][0]
    signal = [item for item in SMMSAdapter(DATASET).load() if item["task_code"] == "SNT-C102-DEMO"][0]
    traction = [item for item in TDMSAdapter(DATASET).load() if item["task_code"] == "TRA-C102-DEMO"][0]
    assert {engineering["corridor_id"], signal["corridor_id"], traction["corridor_id"]} == {"C102"}
    assert engineering["location_start"] < signal["location_end"]
