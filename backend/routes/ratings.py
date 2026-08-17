"""
POST /api/ratings

Body: { "movieId": int, "stars": float, "sessionId": str | null, "userId": int | null }

For this class project, either sessionId (guest) or userId (signed-in)
identifies whose rating this is - real token-based auth is out of scope
here, see routes/auth.py for the simplified scheme used instead.
"""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import insert

from ..database import get_db, ratings

router = APIRouter(prefix="/api/ratings", tags=["ratings"])


class RatingIn(BaseModel):
    movieId: int
    stars: float
    sessionId: Optional[str] = None
    userId: Optional[int] = None


@router.post("")
def submit_rating(payload: RatingIn, db=Depends(get_db)):
    db.execute(insert(ratings).values(
        movie_id=payload.movieId,
        stars=payload.stars,
        session_id=payload.sessionId,
        user_id=payload.userId,
    ))
    db.commit()
    return {"success": True}
