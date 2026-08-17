"""
Basic smoke tests for the backend API. These are written to pass WITHOUT
real trained model artifacts present (degraded mode) - they check the app
starts, /api/health reports the degraded state honestly instead of
crashing, and endpoints that don't need models (ratings, comments, auth)
still work against a fresh SQLite DB.

Once real models/*.pkl and processed_data/train_data.csv exist, add tests
here that check /api/recommendations/top and /personalized return real
data instead of a 503.

Run with: pytest tests/test_backend_routes.py
(requires backend/requirements.txt installed first)
"""
import os
import sys

# Use a dedicated test database so this never touches cinematch.db from a
# real run, and set it before importing backend.main (engine is created at
# import time).
os.environ.setdefault("CINEMATCH_DB_URL", "sqlite:///./test_cinematch.db")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check_reports_degraded_mode_honestly():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    # Without real model artifacts present, this should be False, not crash.
    assert body["models_loaded"] is False


def test_movies_list_returns_empty_list_not_error_when_models_missing():
    resp = client.get("/api/movies")
    assert resp.status_code == 200
    assert resp.json() == []


def test_signin_creates_a_user():
    resp = client.post("/api/auth/signin", json={"email": "test@example.com"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "userId" in body


def test_signin_is_idempotent_for_same_email():
    first = client.post("/api/auth/signin", json={"email": "repeat@example.com"})
    second = client.post("/api/auth/signin", json={"email": "repeat@example.com"})
    assert first.json()["userId"] == second.json()["userId"]


def test_submit_rating_succeeds_for_guest():
    resp = client.post("/api/ratings", json={
        "movieId": 1, "stars": 4.5, "sessionId": "guest-session-abc"
    })
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_submit_and_read_comment():
    submit = client.post("/api/comments", json={
        "movieId": 42, "text": "Loved this one!", "sessionId": "guest-session-xyz"
    })
    assert submit.status_code == 200

    read = client.get("/api/movies/42/comments")
    assert read.status_code == 200
    texts = [c["text"] for c in read.json()]
    assert "Loved this one!" in texts


def test_recommendations_return_503_when_models_not_loaded():
    resp = client.get("/api/recommendations/top")
    assert resp.status_code == 503
