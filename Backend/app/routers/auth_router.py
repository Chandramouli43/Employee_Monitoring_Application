from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.employee_service import get_employee_by_email, verify_password
from app.utils.auth import create_access_token

router = APIRouter()

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT + basic user info.
    """
    user = get_employee_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # ✅ Create JWT with email + role
    access_token = create_access_token(email=user.email, role=user.role)

    # ✅ Return both token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}" if user.first_name else user.name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "designation": getattr(user, "designation", None),
            "department": getattr(user, "department", None),
        },
    }
