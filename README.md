<<<<<<< HEAD
# CineMatch — CS254 Final Project (Group 15)

## Folder structure

```
CineMatch-Project/
├── notebooks/                    # Data Engineer + Recommendation Developer's work
│   ├── data_engineering.ipynb
│   └── recommendation_developer.ipynb
├── data/                         # put Movie_lens_2024.zip here (not included)
├── processed_data/                # OUTPUT of data_engineering.ipynb (empty until run)
├── models/                        # OUTPUT of recommendation_developer.ipynb + recommender.py
├── backend/                       # FastAPI service wiring models + DB to the frontend
│   └── routes/
├── app/                           # Streamlit demo scaffold (local-only, in-memory)
├── movie-recommender-frontend/    # Static HTML/CSS/JS site (the polished deliverable)
├── docs/wireframes/
├── tests/
├── requirements.txt                # for app/ (Streamlit)
└── README-streamlit.md
```

## Status of each piece

| Piece | Status |
|---|---|
| `notebooks/data_engineering.ipynb`, `notebooks/recommendation_developer.ipynb` | Your team's real work, copied in with portability fixes (see below) |
| `notebooks/evaluation.ipynb` | **New** — extracted from your evaluation code (RMSE/MAE, precision/recall@k, popularity baseline, K-Means-via-TruncatedSVD baseline, confusion matrices, learning curves, bias/fairness analysis) into its own runnable notebook |
| `data/` | **Empty** — you need to add the real dataset zip yourself |
| `processed_data/`, `models/*.pkl` | **Empty** — only exist after you run the notebooks against the real dataset |
| `models/recommender.py` | Extracted from the notebook, real code, ready to use |
| `backend/` | Built earlier, syntax-checked, **not executable-tested** (no `fastapi`/`pytest` installed here, no network, no trained artifacts to test against) |
| `movie-recommender-frontend/js/api.js` | **Now actually wired to the backend** via real `fetch()` calls, with automatic fallback to mock data if the backend isn't reachable — see `movie-recommender-frontend/README.md` |
| `app/` (Streamlit) | Built earlier, bugs fixed, in-memory demo only |
| `tests/` | Written earlier, syntax-checked but **not run** |

**Be aware:** because I can't install packages, reach the internet, or run
your actual dataset here, `backend/` and `tests/` are carefully written and
syntax-checked, but the first time your team runs them for real is also the
first time they've actually been executed end-to-end. Budget real debugging
time for that.

## About the large pasted document you shared

At one point you pasted a large block of text that looked like a newer,
consolidated version of your notebook — combining the data engineering
pipeline, modeling, the evaluation TODO 1–7 section, the frontend
`%%writefile` cells, and a few stray package-install cells
(`libarchive`, `pydot`, `cartopy`) all together. That text is **not** the same
file as `notebooks/recommendation_developer.ipynb` in this folder — it only
exists as pasted text, not as an actual `.ipynb` I was given. I could not
edit "your real notebook" directly for that reason.

What I *did* do with it: extracted the evaluation section into the new,
real `notebooks/evaluation.ipynb` described above, since that was genuinely
new content. I also checked the `recommendations.html` code embedded in that
same pasted text against a likely bug (a template literal that appeared to
close early, leaving `await` outside an `async function`) — **the actual
`movie-recommender-frontend/recommendations.html` in this project does not
have that bug**, confirmed via Node's syntax checker.

If your live/working notebook really does contain those stray install cells
and the frontend `%%writefile` cells, you'll want to clean those up yourself
directly in Colab: delete the `libarchive`/`pydot`/`cartopy`/`os.path.isdir('app')`
cells, and either fix or delete the `%%writefile` HTML/CSS/JS cells so they
don't risk overwriting the working copies in `movie-recommender-frontend/`
if someone re-runs them.

## What I changed in `notebooks/`

1. **Fixed the hardcoded zip paths.** `data_engineering.ipynb` had
   `/usr/Movie_lens_2024.zip`, `recommendation_developer.ipynb` (originally
   `NEW_Movie_Engine1.ipynb`) had `/content/Movie_lens_2024.zip`. Both now
   point to `../data/Movie_lens_2024.zip`, so they work from this folder
   structure for anyone on the team, not just whoever's Colab session they
   were written in.
2. **Removed a stray leftover cell** ("AJOKEEEEE") from the recommendation
   notebook.

I did **not** touch the modeling logic itself — RMSE numbers, K-Means
cluster counts, hyperparameter grids, etc. are all exactly as your teammates
built them.

## How the pieces connect (the integration path)

```
data/Movie_lens_2024.zip
        │
        ▼
notebooks/data_engineering.ipynb
        │
        ▼
processed_data/  (train/val/test CSVs, cold-start fallbacks, etc.)
        │
        ▼
notebooks/recommendation_developer.ipynb
        │
        ▼
models/  (*.pkl files + recommender.py)
        │
        ▼
backend/  (FastAPI: loads models/ once, exposes REST API, real SQLite DB
           for users/ratings/comments)
        │
        ▼
movie-recommender-frontend/js/api.js  (swap BACKEND TODO comments for
                                        fetch() calls to backend/)
```

Full endpoint-by-endpoint wiring instructions are in `backend/README.md`.

## The one design decision every teammate should understand

`backend/routes/recommendations.py` routes a request to real SVD+hybrid
recommendations **only if the userId already existed in the training data**.
Every brand-new signup — no matter how many movies they rate in a live demo —
goes through the cold-start path instead (`cold_start_recommend`, genre
cluster-based). This is correct behavior for how SVD works, but it means a
live demo of "sign in, rate a few movies, get personalized picks" will look
noticeably different (cluster-based, not hybrid-quality) for an actual new
user than it does for one of the userIds that was in the original dataset.
Know this going in so nobody is surprised on demo day.

## Two front ends still not reconciled

`app/` (Streamlit) and `movie-recommender-frontend/` (static HTML) are
separate implementations with separate mock data. Only one should become the
real deliverable wired to `backend/` — see each folder's own README for
details. This is still an open team decision, not something I've resolved
for you.

## Still not built

An evaluation/insights page or section for the Evaluation teammate's model
comparison table and bias/fairness visualizations doesn't exist in either
front end yet — flagged in earlier reviews, still outstanding.
=======
# Intro_to_ai_final_project
>>>>>>> de12da9a08cd5bb9d9fd2b6fdd1a8e4bfe470559
