# CineMatch — Streamlit Scaffold

This scaffold accompanies the static HTML frontend (`movie-recommender-frontend/`) and lets you run a quick interactive demo locally, backed by an in-memory Python "backend" — no real database, no persistence between runs.

## Quick start

```bash
python -m pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

## What's in `app/`

| File | Purpose |
|---|---|
| `api.py` | In-memory movie list + rating/comment storage + recommendation heuristics |
| `movie_display.py` | Renders one movie card (gradient poster, rating slider, comment box) |
| `streamlit_app.py` | Main app: search, browse grid, personalized recs, sidebar charts |
| `recommendations.py` | Thin wrapper choosing "top" vs. "personal" recommendation strategy |
| `visualizations.py` | Altair charts: genre distribution, rating histogram |
| `deploy.py` | Helper to launch the app / print run instructions |

## Fixes applied to this scaffold

- **`st.experimental_get_query_params()` → `st.query_params`.** The experimental API is deprecated and can be removed in newer Streamlit releases; `requirements.txt` had no version floor, so a fresh install could break outright. Now pinned to `streamlit>=1.30`, which supports `st.query_params`.
- **`use_column_width=True` → `use_container_width=True`** everywhere images/charts are rendered — same deprecation issue.
- **Consistent absolute imports.** `recommendations.py` used to mix relative (`from .api import`) and absolute (`from app.api import`) imports across the same package, which only works under specific run conditions. Everything now uses `from app.X import`.
- **`movie_display.py` is now actually used.** It previously defined `show_movie_card` / `show_movie_grid` but nothing called them — `streamlit_app.py` duplicated the same logic inline instead. Now `streamlit_app.py` calls `show_movie_grid`, and the rating/comment submission happens directly inside `movie_display.py` via `api.submit_rating` / `api.submit_comment`.
- **Fixed silent default-rating bug.** `st.radio` had no default index, so Streamlit pre-selected the *first* option (1★) for every movie. Clicking "Submit" without deliberately picking a rating would silently save a 1★ you never chose. Rating selectors now use `st.select_slider(..., value=None)`, so no rating is submitted unless you actually pick one.
- **No more external placeholder images.** `via.placeholder.com` requires a live network call per movie card. Replaced with the same CSS-gradient "poster" approach used in the static HTML frontend — works fully offline, and now visually matches the other frontend.
- **Guarded empty-state charts.** Genre/rating charts no longer error if `movies` is empty (e.g. an over-narrow search).

## Known limitations (unchanged, by design at this stage)

- All data is in-memory and resets every time the Streamlit process restarts — there's no real database yet.
- Recommendation logic is a placeholder genre-boost heuristic, not the real collaborative filtering / K-Means models.
- This is a **separate implementation** from the standalone HTML/CSS/JS frontend in `movie-recommender-frontend/`. They are not wired together. Decide as a team which one is the actual deliverable, or keep both (Streamlit for a fast local demo, static HTML for the polished submission) — just don't let them silently drift apart.
