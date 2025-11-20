from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import shutil

from app.core.config import UPLOAD_DIR
from app.core.database import get_db
from app.models.screenshot import Screenshot
from app.utils.auth import get_current_user
from app.schemas.screenshot import ScreenshotResponse

router = APIRouter(prefix="/screenshots", tags=["screenshots"])

UPLOAD_PATH = Path(UPLOAD_DIR) / "screenshots"
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=ScreenshotResponse)
def upload_screenshot(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Upload screenshot captured by monitoring agent."""
    file_path = UPLOAD_PATH / f"{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    screenshot = Screenshot(
        employee_id=current_user.id,
        department_id=current_user.department_id,
        image_path=str(file_path),
        timestamp=datetime.utcnow()
    )
    db.add(screenshot)
    db.commit()
    db.refresh(screenshot)
    return screenshot


@router.get("/me", response_model=list[ScreenshotResponse])
def get_my_screenshots(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Fetch logged-in employee's captured screenshots."""
    return db.query(Screenshot).filter(Screenshot.employee_id == current_user.id).order_by(Screenshot.timestamp.desc()).all()
