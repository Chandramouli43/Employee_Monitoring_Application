from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

# Detect SQLite for connect_args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# ✅ Reliable engine with pre-ping and pooling
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,   # Detect dead connections
    pool_size=10,         # Maintain small connection pool
    max_overflow=20,      # Allow temporary overflow
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
