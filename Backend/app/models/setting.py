from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
# NotificationSetting Model
class NotificationSetting(Base):
    __tablename__ = "notification_settings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)   # e.g. "idle_time", "deadline_reminder"
    enabled = Column(Boolean, default=True)
    channel = Column(String(50), default="in_app")  # in_app, email, slack, etc.
                           