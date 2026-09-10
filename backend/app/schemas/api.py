from datetime import datetime

from pydantic import BaseModel, Field


class OptimizeRequest(BaseModel):
    planning_horizon: str = Field(default="WEEKLY", pattern="^(DAILY|WEEKLY|MONTHLY)$")
    objective: str = "MAXIMIZE_ASSET_AVAILABILITY"


class EmergencyRequest(BaseModel):
    task_id: str = "EMERGENCY-API-001"
    corridor_id: str
    location_start: float
    location_end: float
    department: str
    description: str = "Synthetic emergency defect"
    estimated_duration_minutes: int = Field(default=60, ge=1, le=1440)
    reported_at: datetime | None = None
