from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base
# Leave ModelESS
class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employee.id", ondelete="CASCADE"))  # ✅ FIXED
    approved_by = Column(Integer, ForeignKey("employee.id", ondelete="SET NULL"), nullable=True)  # ✅ optional

    leave_type = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="Pending")
    applied_on = Column(DateTime, default=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leaves")
    approver = relationship("Employee", foreign_keys=[approved_by], back_populates="approved_leaves", viewonly=True)
