from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Float, Integer, String, Time
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import BlockPlanStatus, BlockType


class BlockPlan(Base):
    __tablename__ = "block_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    plan_date: Mapped[date] = mapped_column(Date, index=True)
    corridor_id: Mapped[str] = mapped_column(String(50), index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    block_type: Mapped[BlockType] = mapped_column(SqlEnum(BlockType, name="block_type"))
    status: Mapped[BlockPlanStatus] = mapped_column(SqlEnum(BlockPlanStatus, name="block_plan_status"), default=BlockPlanStatus.DRAFT, index=True)
    optimization_score: Mapped[float | None] = mapped_column(Float)
    utilization_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    task_links: Mapped[list["BlockPlanTask"]] = relationship(back_populates="block_plan", cascade="all, delete-orphan")
