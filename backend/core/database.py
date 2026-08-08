"""SQLAlchemy engine + session factory.

DATABASE_URL controls whether we point at SQLite (default) or PostgreSQL — no
per-engine branching in the codebase beyond `connect_args`. `get_db` is a
FastAPI dependency that yields a scoped session.
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.core.config import settings

if settings.DATABASE_URL.startswith("sqlite"):
    db_file = settings.DATABASE_URL.split("///")[-1]
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
