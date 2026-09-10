from app.services.ingestion.base import SourceAdapter


class TimetableAdapter(SourceAdapter[dict]):
    dataset_key = "trains"
