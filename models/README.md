# models/

`recommender.py` is already here — it's the final, validated model-serving
code extracted directly from `notebooks/recommendation_developer.ipynb`'s
last cell (the one written with `%%writefile recommender.py`). Everything
else in this folder is empty until you run that notebook end-to-end, which
requires `processed_data/` to already be populated (see
`processed_data/README.md`).

Running the notebook produces the following files, which `recommender.py`'s
`load_models()` expects to find in this exact folder:

- `svd_final.pkl`, `knn_item_tuned.pkl`
- `kmeans_users.pkl`, `kmeans_movies.pkl`, `scaler.pkl`
- `genre_columns.pkl`, `global_mean_rating.pkl`, `genre_mean_ratings.pkl`
- `user_genre_matrix.pkl`, `movie_genre_matrix.pkl`, `movies_lookup.pkl`

**Keeping this in sync with the notebook:** don't hand-edit this copy of
`recommender.py` and the notebook's `%%writefile` cell separately — they will
drift apart. Treat *this* file as the canonical one going forward; if you
need to change the recommendation logic, either edit it here and copy the
change back into the notebook cell, or point the notebook's `%%writefile` at
`../models/recommender.py` directly so there's only one copy.

**Unpickling note:** `svd_final.pkl` and `knn_item_tuned.pkl` are
`scikit-surprise` model objects. Unpickling them requires `scikit-surprise`
to be installed in whatever environment loads them — this is already in
`backend/requirements.txt`, but keep the installed version reasonably close
to whatever version trained these files, since scikit-learn/surprise
occasionally break pickle compatibility across major versions.
