from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import BlockType, Department, TaskStatus

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.block_plan_task import BlockPlanTask


class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    source_system: Mapped[str] = mapped_column(String(20), index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"), index=True)
    department: Mapped[Department] = mapped_column(SqlEnum(Department, name="department"), index=True)
    corridor_id: Mapped[str] = mapped_column(String(50), index=True)
    location_start: Mapped[float] = mapped_column(Float)
    location_end: Mapped[float] = mapped_column(Float)
    task_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer)
    criticality: Mapped[float] = mapped_column(Float)
    safety_impact: Mapped[float] = mapped_column(Float)
    urgency: Mapped[float] = mapped_column(Float)
    failure_risk: Mapped[float] = mapped_column(Float)
    availability_impact: Mapped[float] = mapped_column(Float)
    required_block_type: Mapped[BlockType] = mapped_column(SqlEnum(BlockType, name="block_type"))
    required_resources: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[TaskStatus] = mapped_column(SqlEnum(TaskStatus, name="task_status"), default=TaskStatus.PENDING, index=True)
    priority_score: Mapped[float | None] = mapped_column(Float)
    priority_level: Mapped[str | None] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    asset: Mapped["Asset"] = relationship(back_populates="maintenance_tasks")
    plan_links: Mapped[list["BlockPlanTask"]] = relationship(back_populates="maintenance_task")
