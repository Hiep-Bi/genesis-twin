"""Sensor endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/sensors", tags=["Sensors"])


class SensorResponse(BaseModel):
    id: UUID
    sensor_code: str
    sensor_type: str
    unit: str
    threshold_warning: float
    threshold_critical: float
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[SensorResponse])
async def list_sensors(
    machine_id: UUID = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all sensors"""
    from app.models.machine import Sensor
    query = db.query(Sensor)
    
    if machine_id:
        query = query.filter(Sensor.machine_id == machine_id)
    
    return query.offset(skip).limit(limit).all()

