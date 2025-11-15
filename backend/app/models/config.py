"""Configuration models for Production Line Mapping and Material Requirements"""
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base


class ProductionLineMapping(Base):
    """Production Line Mapping - Maps product codes to production lines"""
    __tablename__ = "production_line_mapping"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_code_pattern = Column(String(100), nullable=False, index=True)
    line_code = Column(String(50), nullable=False, index=True)
    line_name = Column(String(255))
    line_type = Column(String(50))  # "machining", "assembly", "packaging", etc.
    priority_base = Column(Integer, default=5)  # Base priority (1-10)
    is_upstream = Column(Boolean, default=False)  # Upstream lines affect downstream
    dependencies = Column(JSON)  # List of dependent line codes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ProductionLineMapping {self.line_code}: {self.product_code_pattern}>"


class LineMaterialRequirement(Base):
    """Line Material Requirements - Maps lines to required materials"""
    __tablename__ = "line_material_requirements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    line_code = Column(String(50), nullable=False, index=True)
    material_code = Column(String(50), nullable=False, index=True)
    required_quantity_per_unit = Column(Float, nullable=False)
    is_critical = Column(Boolean, default=False)  # Critical material
    preferred_location = Column(String(50))  # "main_warehouse" or "external_staging"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('line_code', 'material_code', name='uq_line_material'),
    )
    
    def __repr__(self):
        return f"<LineMaterialRequirement {self.line_code} -> {self.material_code}>"

