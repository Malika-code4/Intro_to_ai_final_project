"""
Minimal backend simulation for the Streamlit app.
Provides in-memory movie data and simple recommendation heuristics.

BACKEND TODO: replace the bodies of these functions with real database /
model calls once the Data Engineer and Recommendation Developer's work is
ready. Keep function names and return shapes the same so streamlit_app.py
and movie_display.py don't need to change.
"""
from typing import List, Dict, Any
import random

GENRES = [
    "Action", "Comedy", "Drama", "Romance", "Sci-Fi",
    "Horror", "Animation", "Thriller", "Documentary", "Fantasy"
]

# Colorful gradient placeholders instead of external placeholder-image URLs.
# Using real network image URLs (e.g. via.placeholder.com) means every
# movie card fails to render if the grading/demo environment has no
# internet access. These are pure CSS, so they always work offline.
POSTER_GRADIENTS = [
    "linear-gradient(160deg,#ff6b6b,#f9d423)",
    "linear-gradient(160deg,#7f7fd5,#86a8e7,#91eae4)",
    "linear-gradient(160deg,#f857a6,#ff5858)",
    "linear-gradient(160deg,#43cea2,#185a9d)",
    "linear-gradient(160deg,#ffb347,#ffcc33)",
    "linear-gradient(160deg,#a18cd1,#fbc2eb)",
    "linear-gradient(160deg,#ff9a9e,#fecfef)",
    "linear-gradient(160deg,#30cfd0,#330867)",
    "linear-gradient(160deg,#f6d365,#fda085)",
    "linear-gradient(160deg,#84fab0,#8fd3f4)",
]

MOVIES = [
    {"id": 1,  "title": "Nebula Drift",        "year": 2021, "genre": "Sci-Fi", "avgRating": 4.6, "ratingsCount": 812},
    {"id": 2,  "title": "Laugh Track",         "year": 2019, "genre": "Comedy", "avgRating": 4.1, "ratingsCount": 530},
    {"id": 3,  "title": "Silent Harbor",       "year": 2020, "genre": "Drama", "avgRating": 4.4, "ratingsCount": 950},
    {"id": 4,  "title": "Crimson Vow",         "year": 2018, "genre": "Romance", "avgRating": 3.9, "ratingsCount": 410},
    {"id": 5,  "title": "Iron Skyline",        "year": 2022, "genre": "Action", "avgRating": 4.7, "ratingsCount": 1320},
    {"id": 6,  "title": "The Quiet House",     "year": 2017, "genre": "Horror", "avgRating": 4.0, "ratingsCount": 289},
    {"id": 7,  "title": "Paper Lantern Town",  "year": 2016, "genre": "Animation", "avgRating": 4.5, "ratingsCount": 670},
    {"id": 8,  "title": "Static Line",         "year": 2023, "genre": "Thriller", "avgRating": 4.3, "ratingsCount": 745},
    {"id": 9,  "title": "Wandering Coastline", "year": 2015, "genre": "Documentary", "avgRating": 4.2, "ratingsCount": 198},
    {"id": 10, "title": "Ember & Ash",         "year": 2021, "genre": "Fantasy", "avgRating": 4.6, "ratingsCount": 860},
]

# attach a poster gradient deterministically to each movie
for _i, _m in enumerate(MOVIES):
    _m["posterGradient"] = POSTER_GRADIENTS[_i % len(POSTER_GRADIENTS)]

# simple in-memory user activity store keyed by session id
USER_RATINGS: Dict[str, Dict[int, float]] = {}
USER_COMMENTS: Dict[str, Dict[int, list]] = {}


def load_movies() -> List[Dict[str, Any]]:
    return MOVIES.copy()


def get_top_recommendations(limit: int = 12) -> List[Dict[str, Any]]:
    return sorted(MOVIES, key=lambda m: (m["avgRating"], m["ratingsCount"]), reverse=True)[:limit]


def get_personalized_recommendations(session_id: str, limit: int = 12) -> List[Dict[str, Any]]:
    """Boost movies that match genres the user liked (rated >=4) and exclude already rated movies."""
    user_ratings = USER_RATINGS.get(session_id, {})
    liked_genres = set()
    for mid, r in user_ratings.items():
        if r >= 4:
            movie = next((m for m in MOVIES if m["id"] == mid), None)
            if movie:
                liked_genres.add(movie["genre"])

    scores = []
    for m in MOVIES:
        if m["id"] in user_ratings:
            continue
        score = m["avgRating"]
        if m["genre"] in liked_genres:
            score += 0.6
        # small random tie-breaker
        score += random.random() * 0.05
        scores.append((score, m))

    scores.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scores][:limit]


def submit_rating(session_id: str, movie_id: int, rating: float):
    USER_RATINGS.setdefault(session_id, {})[movie_id] = rating


def submit_comment(session_id: str, movie_id: int, comment: str):
    if not comment:
        return
    USER_COMMENTS.setdefault(session_id, {}).setdefault(movie_id, []).append(comment)


def get_user_activity(session_id: str):
    return {
        "ratings": USER_RATINGS.get(session_id, {}),
        "comments": USER_COMMENTS.get(session_id, {})
    }
