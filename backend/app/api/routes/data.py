from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Asset, BlockWindow, MaintenanceTask, Train

router = APIRouter(tags=["data"])


def _serialize(model) -> dict:
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


@router.get("/assets")
def list_assets(db: Session = Depends(get_db), corridor: str | None = None, department: str | None = None) -> list[dict]:
    query = select(Asset)
    if corridor:
        query = query.where(Asset.corridor_id == corridor)
    if department:
        query = query.where(Asset.department == department)
    return [_serialize(asset) for asset in db.scalars(query).all()]


@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db), department: str | None = None, priority: str | None = None, status: str | None = None, corridor: str | None = None, limit: int = Query(default=100, ge=1, le=1000), offset: int = Query(default=0, ge=0)) -> dict:
    query = select(MaintenanceTask).offset(offset).limit(limit)
    if department:
        query = query.where(MaintenanceTask.department == department)
    if priority:
        query = query.where(MaintenanceTask.priority_level == priority)
    if status:
        query = query.where(MaintenanceTask.status == status)
    if corridor:
        query = query.where(MaintenanceTask.corridor_id == corridor)
    tasks = db.scalars(query).all()
    return {"items": [_serialize(task) for task in tasks], "limit": limit, "offset": offset}


@router.get("/trains")
def list_trains(db: Session = Depends(get_db), corridor: str | None = None, limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    query = select(Train).limit(limit)
    if corridor:
        query = query.where(Train.corridor_id == corridor)
    return [_serialize(train) for train in db.scalars(query).all()]


@router.get("/blocks")
def list_blocks(db: Session = Depends(get_db), corridor: str | None = None, limit: int = Query(default=100, ge=1, le=1000)) -> list[dict]:
    query = select(BlockWindow).limit(limit)
    if corridor:
        query = query.where(BlockWindow.corridor_id == corridor)
    return [_serialize(block) for block in db.scalars(query).all()]
