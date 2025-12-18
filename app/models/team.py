from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
# Team Model
class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    department = relationship("Department", back_populates="teams")
    employees = relationship("Employee", back_populates="team", cascade="all, delete-orphan")
    productivity = relationship("Productivity", back_populates="team", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="team", cascade="all, delete-orphan")
