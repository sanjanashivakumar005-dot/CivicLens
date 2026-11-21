import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database directory
BASE_DIR = Path(__file__).resolve().parent

# SQLite database location
DATABASE_PATH = BASE_DIR / "civiclens.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# SQLite configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for SQLAlchemy models
Base = declarative_base()