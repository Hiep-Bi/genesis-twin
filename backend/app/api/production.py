"""Production endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/production", tags=["Production"])


class ProductionOrderResponse(BaseModel):
    id: UUID
    order_number: str
    product_code: str
    quantity: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/orders", response_model=List[ProductionOrderResponse])
async def list_production_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List production orders"""
    from app.models.production import ProductionOrder
    return db.query(ProductionOrder).limit(100).all()

