from passlib.context import CryptContext
import os
from app.core.config import settings
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def ensure_export_dir():
    path = settings.EXPORT_DIR
    os.makedirs(path, exist_ok=True)
    return path

def make_export_filename(prefix: str, ext: str):
    dt = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{dt}.{ext}"


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def save_file(file, upload_dir: str, filename: str):
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(file.read())
    return path
