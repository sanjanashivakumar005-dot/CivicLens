
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "civiclens.db"

# --------------------------------------------------
# DATABASE URL
# --------------------------------------------------

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# --------------------------------------------------
# SQLALCHEMY CONFIGURATION
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


# --------------------------------------------------
# DATABASE SESSION
# --------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# --------------------------------------------------
# CONNECTION TEST
# --------------------------------------------------

def test_connection():
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")

        print("✅ CivicLens database connection successful!")
        print(f"📁 Database location: {DATABASE_PATH}")

        return True

    except Exception as error:
        print("❌ Database connection failed!")
        print(f"Error: {error}")

        return False
