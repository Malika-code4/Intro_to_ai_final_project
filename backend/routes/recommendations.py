"""
GET /api/recommendations/top
GET /api/recommendations/personalized?userId=...&genres=Comedy,Action

Routes to the correct model per user status:
- Known user_id that existed in the ORIGINAL TRAINING DATA -> full SVD +
  content hybrid (recommender.get_top_n_hybrid)
- Everyone else (guests, brand-new signups, or a userId we don't
  recognize) -> cold-start path (recommender.cold_start_recommend):
    - with genre signal -> K-Means cluster-based
    - with no signal at all -> global/genre mean fallback

IMPORTANT: signing in does NOT make a user eligible for the SVD hybrid
path. SVD only knows userIds present in train_data.csv at training time.
A real new signup always goes through cold_start_recommend() until a
periodic retrain folds their ratings back into the model - see the
top-level README for why this matters.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from .. import model_state

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _require_models():
    state = model_state.get_state()
    if not state["loaded"]:
        model_state.load()
        state = model_state.get_state()
    if not state["loaded"]:
        raise HTTPException(status_code=503, detail=state["error"])
    return state


@router.get("/top")
def top_recommendations(n: int = 10):
    """Popularity baseline: same list for everyone, no personalization
    needed. Reimplemented here to match notebooks/recommendation_developer.ipynb's
    popularity_baseline() exactly, since that function lives in the
    notebook itself rather than models/recommender.py."""
    state = _require_models()
    train_df = state["train_df"]

    stats = (
        train_df.groupby(["movieId", "title"])
        .agg(mean_rating=("rating", "mean"), num_ratings=("rating", "count"))
        .reset_index()
    )
    reliable = stats[stats["num_ratings"] >= 20]
    result = reliable.sort_values("mean_rating", ascending=False).head(n)

    return [
        {
            "id": int(r.movieId),
            "title": r.title,
            "avgRating": round(float(r.mean_rating), 2),
            "ratingsCount": int(r.num_ratings),
            "source": "popularity",
        }
        for r in result.itertuples()
    ]


@router.get("/personalized")
def personalized_recommendations(
    userId: Optional[int] = Query(default=None),
    genres: Optional[str] = Query(default=None, description="Comma-separated genre names, e.g. Comedy,Action"),
    n: int = 10,
):
    state = _require_models()
    recommender = state["recommender"]
    models = state["models"]
    train_df = state["train_df"]

    known_user_ids = set(train_df["userId"].unique().tolist())

    if userId is not None and userId in known_user_ids:
        result = recommender.get_top_n_hybrid(userId, models, train_df, n=n)
        return [
            {
                "id": int(r.movieId),
                "title": r.title,
                "genre": (r.genres.split("|")[0] if isinstance(r.genres, str) else ""),
                "matchScore": round(float(r.hybrid_score), 3),
                "source": "hybrid",
            }
            for r in result.itertuples()
        ]

    # New signup, guest, or an unrecognized userId -> cold start.
    # Today the frontend only sends genre names with no strength signal,
    # so each selected genre is treated as "rated 5" for clustering
    # purposes. Refine this once the frontend collects real per-genre
    # preference strength during onboarding.
    genre_ratings = {}
    if genres:
        genre_ratings = {g.strip(): 5.0 for g in genres.split(",") if g.strip()}

    result = recommender.cold_start_recommend(genre_ratings, models, train_df, n=n)
    return [
        {
            "id": int(r.movieId),
            "title": r.title,
            "avgRating": round(float(r.mean_rating), 2),
            "ratingsCount": int(r.num_ratings),
            "source": "cold_start",
        }
        for r in result.itertuples()
    ]
