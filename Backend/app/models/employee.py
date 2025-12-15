from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base
# Employee Model
class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120))
    email = Column(String(200), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String(50), default="Employee")  # Employee, Manager, HR, Admin
    contact = Column(String(20))
    designation = Column(String(120))
    profile_picture = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationships
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    department = relationship("Department", back_populates="employees")
    team = relationship("Team", back_populates="employees")

    # Attendance Relationship
    attendances = relationship("Attendance",back_populates="employee",cascade="all, delete-orphan")

    # Leave Relationships
    leaves = relationship("Leave",foreign_keys="[Leave.employee_id]",back_populates="employee",cascade="all, delete-orphan")
    approved_leaves = relationship("Leave",foreign_keys="[Leave.approved_by]",viewonly=True)

    # Activity and productivity tracking
    activities = relationship("Activity", back_populates="employee", cascade="all, delete-orphan")
    productivity = relationship("Productivity", back_populates="employee", cascade="all, delete-orphan")
    screenshots = relationship("Screenshot", back_populates="employee", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="employee", cascade="all, delete-orphan")

    # Metrics
    productivity_score = Column(Float, default=0.0)
    tasks_completed = Column(Integer, default=0)
    hours_logged = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
