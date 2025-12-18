from pydantic import BaseModel
from datetime import datetime

class ScreenshotResponse(BaseModel):
    id: int
    image_path: str
    timestamp: datetime

    class Config:
        from_attributes = True
