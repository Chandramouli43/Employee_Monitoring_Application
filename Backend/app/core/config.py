import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Check your .env file.")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Upload directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/screenshots")
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure folder exists
