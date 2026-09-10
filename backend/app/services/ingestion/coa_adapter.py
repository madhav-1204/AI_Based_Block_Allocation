from app.services.ingestion.base import SourceAdapter


class COAAdapter(SourceAdapter[dict]):
    dataset_key = "block_windows"
