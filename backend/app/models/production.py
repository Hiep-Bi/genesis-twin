"""Production models"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class ProductionOrder(Base):
    """Production Order model"""
    __tablename__ = "production_orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    product_code = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    priority = Column(Integer, default=1)
    scheduled_start = Column(DateTime)
    scheduled_end = Column(DateTime)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="production_order")
    
    def __repr__(self):
        return f"<ProductionOrder {self.order_number}>"


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_order_id = Column(UUID(as_uuid=True), ForeignKey("production_orders.id"))
    product_code = Column(String(50), nullable=False)
    serial_number = Column(String(100), unique=True, nullable=False, index=True)
    qr_code = Column(String(255), unique=True, nullable=False, index=True)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"))
    quality_status = Column(String(20), default="pass")  # pass, fail, rework
    defect_types = Column(JSON)
    manufactured_at = Column(DateTime, default=datetime.utcnow)
    inspected_at = Column(DateTime)
    shipped_at = Column(DateTime)
    
    # Relationships
    production_order = relationship("ProductionOrder", back_populates="products")
    
    def __repr__(self):
        return f"<Product {self.serial_number}>"

