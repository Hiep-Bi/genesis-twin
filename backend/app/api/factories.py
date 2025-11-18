"""Factory management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID, uuid4

from app.core.database import get_db
from app.models.factory import Factory
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/factories", tags=["Factories"])

FALLBACK_FACTORIES = [
    {
        "id": uuid4(),
        "name": "Factory Alpha",
        "location": "Industrial Park East",
        "config": {"lines": 3, "shift": "Morning"},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "id": uuid4(),
        "name": "Factory Beta",
        "location": "Innovation Hub West",
        "config": {"lines": 2, "shift": "Evening"},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
]


class FactoryResponse(BaseModel):
    id: UUID
    name: str
    location: str
    config: dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[FactoryResponse])
async def list_factories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all factories
    """
    factories = db.query(Factory).offset(skip).limit(limit).all()
    if not factories:
        return FALLBACK_FACTORIES
    return factories


@router.get("/{factory_id}", response_model=FactoryResponse)
async def get_factory(
    factory_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get factory by ID
    """
    factory = db.query(Factory).filter(Factory.id == factory_id).first()
    if not factory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factory not found"
        )
    return factory
