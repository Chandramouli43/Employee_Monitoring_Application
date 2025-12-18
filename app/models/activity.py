# app/models/activity.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    employee_id = Column(Integer, ForeignKey("employee.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    # Activity Details
    activity_type = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    activity_metadata = Column(Text, nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=False), default=datetime.utcnow)
    productive = Column(String(50), nullable=True)  # matches 'character varying'

    # Relationships
    employee = relationship("Employee", back_populates="activities")
    department = relationship("Department", back_populates="activities")
    team = relationship("Team", back_populates="activities")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
