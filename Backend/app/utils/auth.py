from datetime import datetime, timedelta
from typing import Optional
import os

from jose import JWTError, jwt
from fastapi import HTTPException, Depends ,Cookie, Header

from sqlalchemy.orm import Session

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import get_db
from app.services.employee_service import get_employee_by_email


SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60



bearer_scheme = HTTPBearer(auto_error=False)  


def create_access_token(email: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token containing both email and role.
    """
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": email, "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    bearer: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    access_cookie: str | None = Cookie(default=None, alias="access_token"),
    db: Session = Depends(get_db)
):
    """
    Accept JWT from:
    - Authorization: Bearer <token>
    - Cookie: access_token=<token>

    Returns the authenticated user object.
    """

    
    token = None

    if bearer and bearer.credentials:
        token = bearer.credentials
    elif access_cookie:
        token = access_cookie

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")

        if not email:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

 
    user = get_employee_by_email(db, email)

    if not user:
        raise credentials_exception

    if role and user.role != role:
        print(f"Syncing role for user {email}: {user.role} -> {role}")
        user.role = role

    return user


def require_roles(*roles: str):
    """
    Dependency to require specific roles for a route.
    Usage:
        @router.get("/admin", dependencies=[Depends(require_roles("Admin"))])
    """

    def role_checker(current_user=Depends(get_current_user)):
        print(f"Checking roles for user {current_user.email}: required={roles}, user_role={current_user.role}")
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Operation not permitted for role '{current_user.role}'",
            )
        return current_user

    return role_checker
