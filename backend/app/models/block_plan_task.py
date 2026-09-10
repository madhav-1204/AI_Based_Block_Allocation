from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class BlockPlanTask(Base):
    __tablename__ = "block_plan_tasks"

    block_plan_id: Mapped[int] = mapped_column(ForeignKey("block_plans.id", ondelete="CASCADE"), primary_key=True)
    maintenance_task_id: Mapped[int] = mapped_column(ForeignKey("maintenance_tasks.id", ondelete="RESTRICT"), primary_key=True)
    department: Mapped[str] = mapped_column(String(30))

    block_plan: Mapped["BlockPlan"] = relationship(back_populates="task_links")
    maintenance_task: Mapped["MaintenanceTask"] = relationship(back_populates="plan_links")
