"""
GET /api/movies
GET /api/movies/search?q=...
GET /api/movies/{movie_id}

Matches the shapes js/api.js expects: movie objects with at least
id, title, genre, avgRating, ratingsCount.
"""
from fastapi import APIRouter, Query, HTTPException

from .. import model_state

router = APIRouter(prefix="/api/movies", tags=["movies"])


def _movie_catalog():
    """Builds a browsable catalog from the trained model's movies_lookup +
    rating stats computed from the training data. Returns an empty list
    (not an error) if models haven't been loaded yet, so the frontend can
    still render an empty state instead of crashing."""
    state = model_state.get_state()
    if not state["loaded"]:
        return []

    movies_lookup = state["models"]["movies_lookup"]
    train_df = state["train_df"]

    stats = (
        train_df.groupby("movieId")["rating"]
        .agg(avgRating="mean", ratingsCount="count")
        .reset_index()
    )

    merged = movies_lookup.reset_index().merge(stats, on="movieId", how="left")
    merged["avgRating"] = merged["avgRating"].fillna(0).round(2)
    merged["ratingsCount"] = merged["ratingsCount"].fillna(0).astype(int)

    catalog = []
    for _, row in merged.iterrows():
        genres = row["genres"].split("|") if isinstance(row["genres"], str) else []
        catalog.append({
            "id": int(row["movieId"]),
            "title": row["title"],
            "genre": genres[0] if genres else "Unknown",
            "genres": genres,
            "avgRating": float(row["avgRating"]),
            "ratingsCount": int(row["ratingsCount"]),
        })
    return catalog


@router.get("")
def get_all_movies():
    return _movie_catalog()


@router.get("/search")
def search_movies(q: str = Query(default="")):
    catalog = _movie_catalog()
    if not q:
        return catalog
    ql = q.lower()
    return [m for m in catalog if ql in m["title"].lower() or ql in m["genre"].lower()]


@router.get("/{movie_id}")
def get_movie_by_id(movie_id: int):
    catalog = _movie_catalog()
    for m in catalog:
        if m["id"] == movie_id:
            return m
    raise HTTPException(status_code=404, detail="Movie not found")
