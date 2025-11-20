# app/models/productivity.py
from sqlalchemy import Column, Integer, Float, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import date
from app.core.database import Base

# Productivity Model
class Productivity(Base):
    __tablename__ = "productivity"

    # ---------------------------
    # Primary Key
    # ---------------------------
    id = Column(Integer, primary_key=True, index=True)

    # ---------------------------
    # Foreign Keys
    # ---------------------------
    employee_id = Column(Integer, ForeignKey("employee.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # ---------------------------
    # Productivity Metrics
    # ---------------------------
    # ✅ Automatically sets today's date as default for 'period'
    period = Column(String(20), nullable=False, default=lambda: str(date.today()))  
    average_score = Column(Float, default=0.0)        # 0-100
    tasks_completed = Column(Integer, default=0)
    hours_logged = Column(Float, default=0.0)
    score = Column(Float, nullable=True)              # Optional individual score
    date = Column(Date, nullable=True)                # Specific date if needed

    # ---------------------------
    # Relationships
    # ---------------------------
    employee = relationship("Employee", back_populates="productivity")
    department = relationship("Department", back_populates="productivity")
    team = relationship("Team", back_populates="productivity")

    # ---------------------------
    # Timestamp
    # ---------------------------
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
