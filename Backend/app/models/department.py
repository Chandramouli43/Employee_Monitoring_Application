from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
# Department Model
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)

    # Relationships
    teams = relationship("Team", back_populates="department", cascade="all, delete-orphan")
    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")
    productivity = relationship("Productivity", back_populates="department", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="department", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="department", cascade="all, delete-orphan")

    class Config:
        from_attributes = True
