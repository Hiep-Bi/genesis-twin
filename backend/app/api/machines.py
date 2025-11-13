"""Machine management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.machine import Machine, Sensor
from app.models.user import User
from app.api.dependencies import get_current_user, require_engineer

router = APIRouter(prefix="/machines", tags=["Machines"])


# Pydantic models
class MachineCreate(BaseModel):
    machine_code: str
    machine_type: str
    name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    year_installed: Optional[int] = None
    specifications: Optional[dict] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None


class MachineUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    specifications: Optional[dict] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None


class MachineResponse(BaseModel):
    id: UUID
    machine_code: str
    machine_type: str
    name: str
    manufacturer: Optional[str]
    model: Optional[str]
    status: str
    position_x: Optional[float]
    position_y: Optional[float]
    position_z: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MachineStats(BaseModel):
    total_machines: int
    running: int
    idle: int
    maintenance: int
    error: int


# Endpoints
@router.get("/", response_model=List[MachineResponse])
async def list_machines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    machine_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all machines with optional filtering
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **machine_type**: Filter by machine type (CNC, Robot, AGV, Assembly)
    - **status**: Filter by status (idle, running, maintenance, error)
    """
    query = db.query(Machine)
    
    if machine_type:
        query = query.filter(Machine.machine_type == machine_type)
    
    if status:
        query = query.filter(Machine.status == status)
    
    machines = query.offset(skip).limit(limit).all()
    return machines


@router.get("/stats", response_model=MachineStats)
async def get_machine_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get machine statistics"""
    total = db.query(func.count(Machine.id)).scalar()
    running = db.query(func.count(Machine.id)).filter(Machine.status == "running").scalar()
    idle = db.query(func.count(Machine.id)).filter(Machine.status == "idle").scalar()
    maintenance = db.query(func.count(Machine.id)).filter(Machine.status == "maintenance").scalar()
    error = db.query(func.count(Machine.id)).filter(Machine.status == "error").scalar()
    
    return {
        "total_machines": total,
        "running": running,
        "idle": idle,
        "maintenance": maintenance,
        "error": error
    }


@router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine(
    machine_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get machine by ID"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    return machine


@router.post("/", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    machine_data: MachineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    """Create a new machine (Engineer role required)"""
    # Check if machine code already exists
    existing = db.query(Machine).filter(Machine.machine_code == machine_data.machine_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Machine code already exists"
        )
    
    machine = Machine(**machine_data.dict())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    
    return machine


@router.put("/{machine_id}", response_model=MachineResponse)
async def update_machine(
    machine_id: UUID,
    machine_data: MachineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    """Update machine (Engineer role required)"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    # Update fields
    for field, value in machine_data.dict(exclude_unset=True).items():
        setattr(machine, field, value)
    
    machine.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(machine)
    
    return machine


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(
    machine_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    """Delete machine (Engineer role required)"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Machine not found"
        )
    
    db.delete(machine)
    db.commit()
    
    return None

