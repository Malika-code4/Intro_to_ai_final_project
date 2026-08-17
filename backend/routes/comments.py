"""
POST /api/comments
GET  /api/movies/{movie_id}/comments
"""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import insert, select

from ..database import get_db, comments as comments_table

router = APIRouter(prefix="/api", tags=["comments"])


class CommentIn(BaseModel):
    movieId: int
    text: str
    sessionId: Optional[str] = None
    userId: Optional[int] = None


@router.post("/comments")
def submit_comment(payload: CommentIn, db=Depends(get_db)):
    db.execute(insert(comments_table).values(
        movie_id=payload.movieId,
        text=payload.text,
        session_id=payload.sessionId,
        user_id=payload.userId,
    ))
    db.commit()
    return {"success": True}


@router.get("/movies/{movie_id}/comments")
def get_comments(movie_id: int, db=Depends(get_db)):
    rows = db.execute(
        select(comments_table)
        .where(comments_table.c.movie_id == movie_id)
        .order_by(comments_table.c.created_at.desc())
    ).fetchall()
    return [
        {"user": f"user_{r.user_id}" if r.user_id else "Guest", "text": r.text}
        for r in rows
    ]
