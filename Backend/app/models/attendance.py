from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

# Attendance Model
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(
        Integer,
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Core fields
    date = Column(Date, nullable=False, default=func.current_date())
    login_time = Column(DateTime(timezone=True), nullable=True)
    logout_time = Column(DateTime(timezone=True), nullable=True)
    total_hours = Column(String(50), default="0h 0m")

    # Status: "Present", "Absent", "On Leave", "Half Day", "Not Punched In"
    status = Column(String(50), default="Not Punched In")

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="attendances")
