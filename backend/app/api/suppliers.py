"""Supplier management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID, uuid4

from app.core.database import get_db
from app.models.supplier import Supplier
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

FALLBACK_SUPPLIERS = [
    {
        "id": uuid4(),
        "supplier_code": "SUP-001",
        "name": "Global Components Inc.",
        "contact_info": {"email": "contact@global.com", "phone": "111-222-3333"},
        "rating": 4.5,
        "performance_score": 0.92,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": uuid4(),
        "supplier_code": "SUP-002",
        "name": "Local Raw Materials",
        "contact_info": {"email": "info@localrm.com", "phone": "444-555-6666"},
        "rating": 3.9,
        "performance_score": 0.85,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]


class SupplierResponse(BaseModel):
    id: UUID
    supplier_code: str
    name: str
    contact_info: Optional[dict]
    rating: float
    performance_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SupplierResponse])
async def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all suppliers
    """
    suppliers = db.query(Supplier).offset(skip).limit(limit).all()
    if not suppliers:
        return FALLBACK_SUPPLIERS
    return suppliers


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get supplier by ID
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    return supplier
