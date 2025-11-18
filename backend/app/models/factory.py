"""Factory model"""
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class Factory(Base):
    """Factory model"""
    __tablename__ = "factories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    location = Column(String(255))
    
    # Relationships
    machines = relationship("Machine", back_populates="factory")

    def __repr__(self):
        return f"<Factory {self.name}>"
