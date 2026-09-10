from app.services.ingestion.base import SourceAdapter


class GoodsForecastAdapter(SourceAdapter[dict]):
    dataset_key = "goods_forecasts"
