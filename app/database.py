"""
Database setup. Uses SQLite by default (zero-config, file-based) so the team
can run this immediately with no external database to install. To switch to
PostgreSQL later (e.g. for deployment), just change DATABASE_URL below to a
Postgres connection string — nothing else in the codebase needs to change.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eduverse.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
