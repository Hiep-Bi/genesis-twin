"""Material management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID, uuid4

from app.core.database import get_db
from app.models.supplier import Material
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/materials", tags=["Materials"])

FALLBACK_MATERIALS = [
    {
        "id": uuid4(),
        "material_code": "MAT-001",
        "name": "Linh kiện A",
        "supplier_id": None,
        "unit": "pcs",
        "unit_price": 10.5,
        "carbon_footprint_per_unit": 0.8,
        "created_at": datetime.utcnow(),
    },
    {
        "id": uuid4(),
        "material_code": "MAT-002",
        "name": "Linh kiện B",
        "supplier_id": None,
        "unit": "pcs",
        "unit_price": 8.2,
        "carbon_footprint_per_unit": 0.6,
        "created_at": datetime.utcnow(),
    },
]


class MaterialResponse(BaseModel):
    id: UUID
    material_code: str
    name: str
    supplier_id: Optional[UUID]
    unit: Optional[str]
    unit_price: Optional[float]
    carbon_footprint_per_unit: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[MaterialResponse])
async def list_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all materials
    """
    materials = db.query(Material).offset(skip).limit(limit).all()
    if not materials:
        return FALLBACK_MATERIALS
    return materials


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get material by ID
    """
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    return material
