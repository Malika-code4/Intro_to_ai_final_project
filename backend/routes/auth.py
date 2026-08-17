"""
POST /api/auth/signin
POST /api/notifications/subscribe

Simplified auth for a class project: no passwords, no JWTs. Signing in
just means "we know this email" -> creates a user row if new, returns
their user_id. The frontend is expected to hold onto that user_id and
send it on subsequent requests (ratings, comments, personalized recs).

This is intentionally NOT production-grade auth. Replace with a real
auth provider (magic links, OAuth, etc.) before handling real user data.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, insert, update

from ..database import get_db, users

router = APIRouter(prefix="/api", tags=["auth"])


class SignInIn(BaseModel):
    email: EmailStr


@router.post("/auth/signin")
def sign_in(payload: SignInIn, db=Depends(get_db)):
    existing = db.execute(select(users).where(users.c.email == payload.email)).first()
    if existing:
        return {"success": True, "userId": existing.id, "email": existing.email}

    result = db.execute(insert(users).values(email=payload.email, notifications_enabled=0))
    db.commit()
    return {"success": True, "userId": result.inserted_primary_key[0], "email": payload.email}


class NotifyIn(BaseModel):
    userId: int


@router.post("/notifications/subscribe")
def subscribe_notifications(payload: NotifyIn, db=Depends(get_db)):
    db.execute(update(users).where(users.c.id == payload.userId).values(notifications_enabled=1))
    db.commit()
    return {"success": True}
