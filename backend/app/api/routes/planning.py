from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Asset, BlockWindow, GoodsForecast, MaintenanceTask, Resource, Train
from app.schemas.api import EmergencyRequest, OptimizeRequest
from app.services.analytics import calculate_analytics
from app.services.planning import EmergencyReplanner, PlanningRequest, PlanningService

router = APIRouter(tags=["planning"])


def _records(db: Session) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    assets = {asset.id: asset for asset in db.scalars(select(Asset)).all()}
    tasks = []
    for task in db.scalars(select(MaintenanceTask)).all():
        tasks.append({"task_id": task.task_code, "department": task.department.value, "corridor_id": task.corridor_id, "location_start": task.location_start, "location_end": task.location_end, "estimated_duration_minutes": task.estimated_duration_minutes, "required_block_type": task.required_block_type.value, "priority_score": task.priority_score or 0, "due_at": task.due_at.isoformat(), "status": task.status.value, "asset_health_score": assets[task.asset_id].health_score})
    trains = [{"train_number": train.train_number, "corridor_id": train.corridor_id, "start_time": train.start_time, "end_time": train.end_time} for train in db.scalars(select(Train)).all()]
    blocks = [{"corridor_id": block.corridor_id, "date": block.date.isoformat(), "start_time": block.start_time.isoformat(), "end_time": block.end_time.isoformat(), "block_type": block.block_type.value, "available": block.available} for block in db.scalars(select(BlockWindow)).all()]
    forecasts = [{"corridor_id": item.corridor_id, "date": item.date.isoformat(), "traffic_density": item.traffic_density.value} for item in db.scalars(select(GoodsForecast)).all()]
    resources = [{"resource_code": resource.resource_code, "department": resource.department.value, "resource_type": resource.resource_type, "capacity": resource.capacity} for resource in db.scalars(select(Resource)).all()]
    return tasks, trains, blocks, forecasts, resources


@router.post("/optimize")
def optimize(request: OptimizeRequest, db: Session = Depends(get_db)) -> dict:
    tasks, trains, blocks, forecasts, resources = _records(db)
    tasks.extend(request.tasks)
    plan = PlanningService().generate_plan(tasks, trains, blocks, forecasts, resources, PlanningRequest(request.planning_horizon, request.objective))
    return PlanningService.plan_summary(plan)


@router.get("/analytics")
def analytics(db: Session = Depends(get_db)) -> dict:
    tasks, trains, blocks, forecasts, resources = _records(db)
    plan = PlanningService().generate_plan(tasks, trains, blocks, forecasts, resources)
    return calculate_analytics(tasks, blocks, plan)


@router.post("/simulation/emergency")
def emergency(request: EmergencyRequest, db: Session = Depends(get_db)) -> dict:
    tasks, trains, blocks, _, resources = _records(db)
    emergency_task = request.model_dump()
    emergency_task["reported_at"] = request.reported_at or datetime.now().astimezone()
    result = EmergencyReplanner().replan(emergency_task, tasks, trains, blocks)
    return {"emergency_task": result.emergency_task, "old_plan": PlanningService.plan_summary(result.old_plan), "new_plan": PlanningService.plan_summary(result.new_plan), "changed_task_ids": result.changed_task_ids, "explanation": result.explanation}
