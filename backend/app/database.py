"""
Database setup for the inventory system.

We use SQLite locally because it needs zero configuration.
On Render/Railway you can swap DATABASE_URL to PostgreSQL later if needed.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default file sits next to the app; override via env var in Docker/cloud
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")

# SQLite needs this flag when used from multiple threads (FastAPI workers)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Each request gets its own session - standard FastAPI pattern
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class all our table models inherit from
Base = declarative_base()


def get_db():
    """
    Dependency injected into route handlers.
    Opens a session, yields it, then closes even if something blows up.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
