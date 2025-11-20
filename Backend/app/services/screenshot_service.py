from sqlalchemy.orm import Session
from app.models.screenshot import Screenshot
from app.utils.helpers import save_file
from datetime import datetime
import os

def save_screenshot(db: Session, employee_id: int, file):
    filename = f"{employee_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.png"
    path = save_file(file, os.getenv("UPLOAD_DIR", "uploads/screenshots"), filename)
    screenshot = Screenshot(employee_id=employee_id, file_path=path)
    db.add(screenshot)
    db.commit()
    db.refresh(screenshot)
    return screenshot
