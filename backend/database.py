"""
SQLite-backed persistence layer for CineMatch.

Replaces:
- movie-recommender-frontend/js/state.js's use of sessionStorage
- app/api.py's in-memory USER_RATINGS / USER_COMMENTS dicts

Uses SQLAlchemy Core (not the full ORM) to keep this readable for a class
project. Swap DATABASE_URL for a real Postgres/MySQL URL later without
touching anything else in backend/.
"""
import os
import datetime
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, Float, String,
    DateTime, ForeignKey,
)
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("CINEMATCH_DB_URL", "sqlite:///./cinematch.db")

# check_same_thread=False is required for SQLite when FastAPI serves
# requests from a thread pool; harmless for other database backends.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", String, unique=True, nullable=False),
    Column("notifications_enabled", Integer, default=0),  # 0/1 boolean
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

ratings = Table(
    "ratings", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    # user_id is null for guest ratings; session_id ties a guest's
    # ratings together for the duration of their browser session, mirroring
    # what js/state.js did client-side with sessionStorage.
    Column("user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("session_id", String, nullable=True),
    Column("movie_id", Integer, nullable=False),
    Column("stars", Float, nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)

comments = Table(
    "comments", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("session_id", String, nullable=True),
    Column("movie_id", Integer, nullable=False),
    Column("text", String, nullable=False),
    Column("created_at", DateTime, default=datetime.datetime.utcnow),
)


def init_db():
    """Call once at app startup. Creates tables if they don't exist yet."""
    metadata.create_all(engine)


SessionLocal = sessionmaker(bind=engine)


def get_db():
    """FastAPI dependency: yields a DB connection, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
