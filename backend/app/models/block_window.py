from datetime import date, time

from sqlalchemy import Date, Integer, String, Time
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.enums import BlockType


class BlockWindow(Base):
    __tablename__ = "block_windows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    corridor_id: Mapped[str] = mapped_column(String(50), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    block_type: Mapped[BlockType] = mapped_column(SqlEnum(BlockType, name="block_type"))
    available: Mapped[bool] = mapped_column(default=True, index=True)
    maximum_duration_minutes: Mapped[int] = mapped_column(Integer)
