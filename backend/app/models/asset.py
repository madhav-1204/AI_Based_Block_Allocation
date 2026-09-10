from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.enums import AssetType, Department


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    asset_type: Mapped[AssetType] = mapped_column(SqlEnum(AssetType, name="asset_type"), index=True)
    department: Mapped[Department] = mapped_column(SqlEnum(Department, name="department"), index=True)
    corridor_id: Mapped[str] = mapped_column(String(50), index=True)
    location_start: Mapped[float] = mapped_column(Float)
    location_end: Mapped[float] = mapped_column(Float)
    criticality: Mapped[float] = mapped_column(Float)
    health_score: Mapped[float] = mapped_column(Float)
    installation_date: Mapped[date | None] = mapped_column(Date)
    last_maintenance_date: Mapped[date | None] = mapped_column(Date)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    operational_importance: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    maintenance_tasks: Mapped[list["MaintenanceTask"]] = relationship(back_populates="asset")
