"""System setting database model"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(String)
    updated_at = Column(DateTime(timezone=True), default=datetime.now)

