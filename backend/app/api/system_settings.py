"""System settings endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID # SystemSettings doesn't have UUID, so this is just here for consistency if needed later

from app.core.database import get_db
from app.models.system_setting import SystemSetting # Assuming this model will be created
from app.models.user import User
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/settings", tags=["System Settings"])


class SystemSettingResponse(BaseModel):
    key: str
    value: dict
    description: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SystemSettingResponse])
async def list_system_settings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all system settings
    """
    settings = db.query(SystemSetting).offset(skip).limit(limit).all()
    return settings


@router.get("/{setting_key}", response_model=SystemSettingResponse)
async def get_system_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system setting by key
    """
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System setting not found"
        )
    return setting
