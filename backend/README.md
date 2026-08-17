# CineMatch Backend

FastAPI service that wires the trained models (`models/`) and processed data
(`processed_data/`) to a real SQLite database, exposing the REST API that
`movie-recommender-frontend/js/api.js` expects.

## Setup

```bash
cd CineMatch-Project
pip install -r backend/requirements.txt
```

## Before you can get real recommendations

This API starts even without trained models present ("degraded mode") so the
rest of the team can develop against it early - but `/api/recommendations/*`
will return `503` until real artifacts exist. To populate them:

1. Put the real dataset zip at `data/Movie_lens_2024.zip`.
2. Run `notebooks/data_engineering.ipynb` end-to-end -> populates `processed_data/`.
3. Run `notebooks/recommendation_developer.ipynb` end-to-end -> produces the
   `.pkl` files this API expects in `models/` (see `models/README.md` for the
   exact file list).
4. Restart the API - `/api/health` will report `"models_loaded": true` once
   everything is found.

## Run it

```bash
uvicorn backend.main:app --reload --port 8000
```

Visit `http://localhost:8000/api/health` to confirm it's up, and
`http://localhost:8000/docs` for interactive API docs (FastAPI generates this
automatically from the route type hints).

## Connecting the static frontend

`movie-recommender-frontend/js/api.js` is **already wired up** to call this
API — no manual editing needed. It defaults to `http://localhost:8000`
(matching the `uvicorn` command above); change the `API_BASE_URL` constant
at the top of that file if you run the backend somewhere else.

If the backend isn't running (or `/api/recommendations/*` returns 503
because `models/` isn't populated yet), `api.js` automatically falls back to
mock data instead of breaking the page — check your browser's console for
`[api.js] ... failed, using mock data instead` warnings to tell which mode
you're in.

In a separate terminal, serve the static site so it can call this API over
real HTTP (not `file://`, which some browsers block from making fetch calls):

```bash
cd movie-recommender-frontend
python -m http.server 5500
```

Then open `http://localhost:5500` — with the backend also running, ratings/
comments/sign-in now hit the real API, not sessionStorage-only mock logic.

Endpoint reference (what `api.js` actually calls):

| Frontend function | Backend route |
|---|---|
| `getAllMovies()` | `GET /api/movies` |
| `searchMovies(q)` | `GET /api/movies/search?q=...` |
| `getMovieById(id)` | `GET /api/movies/{id}` |
| `submitRating(movieId, stars)` | `POST /api/ratings` |
| `submitComment(movieId, text)` | `POST /api/comments` |
| `getComments(movieId)` | `GET /api/movies/{movieId}/comments` |
| `getTopRecommendations()` | `GET /api/recommendations/top` |
| `getPersonalizedRecommendations()` | `GET /api/recommendations/personalized?userId=...&genres=...` |
| `signInWithEmail(email)` | `POST /api/auth/signin` |
| `subscribeToNotifications()` | `POST /api/notifications/subscribe` |

Once this is wired up, `js/mockData.js` and `js/state.js`'s `sessionStorage`
calls are no longer needed for anything the backend now owns - `state.js` can
be trimmed down to just holding onto the current `userId`/`sessionId` the
backend returned.

## The cold-start routing decision (read this before demoing)

`GET /api/recommendations/personalized` does **not** just check "is this user
signed in." It checks whether their `userId` exists in the ORIGINAL TRAINING
DATA (`processed_data/train_data.csv`). If yes, they get true SVD + content
hybrid recommendations. If no - which includes literally every brand-new
signup - they're routed to the cold-start path instead
(`recommender.cold_start_recommend`, cluster-based if they've picked genres,
mean-based fallback if not).

This matters for your demo: **a freshly signed-up user rating a few movies in
the demo will NOT immediately get SVD-quality hybrid recommendations**,
because SVD is a batch-trained matrix factorization that doesn't know about
users who didn't exist at training time. It still degrades gracefully
(cold-start is a real, working recommendation path), just don't be surprised
if it looks less impressive than the version a known training-set user gets.
Retraining periodically to fold in new users is future work, not implemented
here.

## Known simplifications (documented on purpose, not hidden bugs)

- **No password auth.** `/api/auth/signin` just looks up-or-creates a user by
  email. Fine for a class project; replace before handling anything real.
- **Genre preference strength isn't collected yet.** `/api/recommendations/personalized?genres=Comedy,Action`
  treats every selected genre as an implicit "rated 5," since the frontend
  doesn't currently collect a strength/intensity signal during onboarding.
- **CORS is wide open** (`allow_origins=["*"]`) for local development
  convenience. Tighten this to your actual frontend's origin before deploying
  anywhere public.
