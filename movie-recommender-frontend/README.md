# CineMatch — Front-End Only Prototype

Standalone HTML/CSS/JS front end for the Movie Recommendation Engine. No build tools, no server required — just open `index.html` in a browser, or serve the folder with any static file server.

## How to run it

Easiest: double-click `index.html`, or run a simple local server from this folder:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Pages

| File | Purpose |
|---|---|
| `index.html` | Landing page explaining guest vs. signed-in flow |
| `browse.html` | Search/filter movies, click a card to rate + comment |
| `signin.html` | Simulated email sign-in + notification opt-in |
| `recommendations.html` | Sidebar "your recent likes" summary + genre/sort filters, two tabs: "Top overall" and "Because you liked..." (personalized) |

## How guest vs. signed-in works right now

All activity (ratings, comments, signed-in email, notification opt-in) is stored in the browser's `sessionStorage`, not a real database. That's intentional for this front-end-only stage, and it already matches the product requirement that **guest activity disappears when the browser tab closes** — `sessionStorage` does that automatically. Signing in doesn't currently persist anything server-side either, since there's no backend yet.

## Connecting the real backend — now wired up

`js/api.js` now calls the real backend (`../backend/`) via `fetch()` first, for every endpoint. **If that call fails** — the backend isn't running, or `models/` isn't populated yet so `/api/recommendations/*` returns a 503 — each function silently falls back to the original mock-data behavior instead of breaking the page, and logs a warning to the browser console (`[api.js] getAllMovies failed, using mock data instead: ...`) so you can tell which mode you're in.

**To point this at your backend:** edit the `API_BASE_URL` constant at the top of `js/api.js` (defaults to `http://localhost:8000`, matching `backend/README.md`'s run instructions).

**To confirm it's actually hitting the real backend and not silently falling back:** open your browser's dev tools console while using the site. No `[api.js] ... failed` warnings means everything is talking to the real API.

`js/state.js` now also tracks a `sessionId` (auto-generated, stable per guest session) and a `userId` (set after a successful sign-in), which get sent with every rating/comment/recommendation request so the backend knows whose activity it is — this replaces what used to be purely local, backend-less bookkeeping.

Once you're confident the backend is fully wired and always available, `js/mockData.js` and the fallback branches in `js/api.js` can be deleted — they're kept for now purely so the frontend still works standalone if the backend isn't running.

## Simulated email notification flow

Since there's no backend to send real email yet, `signin.html` fakes it: after enabling notifications, a toast pops up after a short delay simulating "you got an email," with a button that mimics clicking the email link — it sends you to `recommendations.html?from=email`, which shows a small "welcome back" banner and jumps straight to the personalized tab. When real email is wired up, that link would point to the same URL pattern with a real auth token instead of `?from=email`.

## Known placeholders to swap out later

- **Posters**: colorful CSS gradients labeled with the title, not real poster images (see `POSTER_GRADIENTS` in `js/mockData.js`). Swap for real image URLs once available.
- **Personalized recommendation logic**: `API.getPersonalizedRecommendations()` currently just matches genres from movies you rated 4★+. This is a stand-in for the real collaborative filtering + K-Means model.
- **"Liked" detection for the recommendations sidebar**: `AppState.getLikedMovies()` treats a movie as "liked" if it was rated 4★+, OR if a comment on it contains a positive word (love/great/best/amazing/favorite/loved). This is a simple heuristic, not real sentiment analysis — swap for a proper NLP pass if the team wants more accurate comment-based signal.
- **24 mock movies** in `js/mockData.js` — replace with real MovieLens/IMDb-backed data via the API.
