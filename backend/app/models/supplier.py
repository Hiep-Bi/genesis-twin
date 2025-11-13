"""Supplier and Material models"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Supplier(Base):
    """Supplier model"""
    __tablename__ = "suppliers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    contact_info = Column(JSON)
    rating = Column(Float, default=0.0)
    performance_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    materials = relationship("Material", back_populates="supplier")
    
    def __repr__(self):
        return f"<Supplier {self.supplier_code}>"


class Material(Base):
    """Material model"""
    __tablename__ = "materials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id"))
    unit = Column(String(20))
    unit_price = Column(Float)
    carbon_footprint_per_unit = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="materials")
    
    def __repr__(self):
        return f"<Material {self.material_code}>"

