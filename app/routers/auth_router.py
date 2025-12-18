# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.employee_service import get_employee_by_email, verify_password
from app.utils.auth import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):

    # Validate user credentials
    user = get_employee_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Generate JWT token
    access_token = create_access_token(email=user.email, role=user.role)

    # Build clean user response (avoid ORM relationship issues)
    name = (
        (f"{user.first_name or ''} {user.last_name or ''}").strip()
        if (user.first_name or user.last_name)
        else (user.name or "")
    )

    dept_value = None
    if getattr(user, "department", None) is not None:
        # choose what you want to expose → name or id
        dept_value = getattr(user.department, "name", None)
        # dept_value = getattr(user.department, "id", None)  # alternative

    user_dict = {
        "id": user.id,
        "name": name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "designation": getattr(user, "designation", None),
        "department": dept_value,
    }

    # Convert to Pydantic response model
    user_payload = UserResponse.model_validate(user_dict)

    # Set HTTP-Only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,  # change to True in HTTPS production
        path="/",
        max_age=3600,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_payload,
    }
