from datetime import date, time

from sqlalchemy import Date, Integer, String, Time
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.enums import TrafficDensity


class GoodsForecast(Base):
    __tablename__ = "goods_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    corridor_id: Mapped[str] = mapped_column(String(50), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    time_window_start: Mapped[time] = mapped_column(Time)
    time_window_end: Mapped[time] = mapped_column(Time)
    expected_goods_trains: Mapped[int] = mapped_column(Integer)
    traffic_density: Mapped[TrafficDensity] = mapped_column(SqlEnum(TrafficDensity, name="traffic_density"))
