from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import shutil
from typing import List
from fastapi import Query
from app.utils.auth import require_roles
from app.core.config import UPLOAD_DIR
from app.core.database import get_db
from app.models.screenshot import Screenshot
from app.utils.auth import get_current_user
from app.schemas.screenshot import ScreenshotResponse

router = APIRouter(prefix="/screenshots", tags=["screenshots"])

UPLOAD_PATH = Path(UPLOAD_DIR) / "screenshots"
UPLOAD_PATH.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=ScreenshotResponse)
def upload_screenshot(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    filename = Path(file.filename).name.strip()  # ✅ sanitize

    file_path = UPLOAD_PATH / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        print(f"Saved file to {file_path}")

    screenshot = Screenshot(
        employee_id=current_user.id,
        department_id=current_user.department_id,
        image_path=f"uploads/screenshots/{filename}",  # ✅ URL-safe
        timestamp=datetime.utcnow()
    )

    db.add(screenshot)
    db.commit()
    db.refresh(screenshot)
    return screenshot

@router.get(
    "/{employee_id}",
    response_model=List[ScreenshotResponse],
)
def get_employee_screenshots(
    employee_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(15, le=50),
    db: Session = Depends(get_db),
    _: object = Depends(require_roles("Admin")),
):
    """
    Fetch screenshots for an employee with pagination.
    Default: first 15 screenshots.
    """

    offset = (page - 1) * limit

    screenshots = (
        db.query(Screenshot)
        .filter(Screenshot.employee_id == employee_id)
        .order_by(Screenshot.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return screenshots