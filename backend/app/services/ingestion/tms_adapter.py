from app.services.ingestion.base import SourceAdapter


class TMSAdapter(SourceAdapter[dict]):
    dataset_key = "maintenance_tasks"

    def load(self) -> list[dict]:
        return [record for record in super().load() if record["source_system"] == "TMS"]
