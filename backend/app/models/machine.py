"""Machine and Sensor models"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Machine(Base):
    """Machine model"""
    __tablename__ = "machines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"))
    machine_code = Column(String(50), unique=True, nullable=False, index=True)
    machine_type = Column(String(50), nullable=False)  # CNC, Robot, AGV, Assembly
    name = Column(String(255), nullable=False)
    manufacturer = Column(String(255))
    model = Column(String(255))
    year_installed = Column(Integer)
    specifications = Column(JSON)
    position_x = Column(Float)
    position_y = Column(Float)
    position_z = Column(Float)
    status = Column(String(20), default="idle")  # idle, running, maintenance, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sensors = relationship("Sensor", back_populates="machine", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Machine {self.machine_code}>"


class Sensor(Base):
    """Sensor model"""
    __tablename__ = "sensors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id", ondelete="CASCADE"))
    sensor_code = Column(String(50), unique=True, nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False)  # temperature, vibration, pressure, energy
    unit = Column(String(20))
    min_value = Column(Float)
    max_value = Column(Float)
    threshold_warning = Column(Float)
    threshold_critical = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    machine = relationship("Machine", back_populates="sensors")
    
    def __repr__(self):
        return f"<Sensor {self.sensor_code}>"

