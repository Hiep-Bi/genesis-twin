"""AI Prediction database model"""
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.core.database import Base


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_type = Column(String(50), nullable=False)
    target_id = Column(UUID(as_uuid=True), nullable=True) # e.g., machine_id, product_id
    prediction_data = Column(JSONB, nullable=False)
    confidence_score = Column(Float)
    actual_outcome = Column(JSONB)
    accuracy = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    prediction_time = Column(DateTime(timezone=True))
    outcome_time = Column(DateTime(timezone=True))

