import os
import pickle
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")


# Load trained SVD model
with open(os.path.join(MODELS_DIR, "svd_final.pkl"), "rb") as f:
    svd = pickle.load(f)


# Load movie lookup data
with open(os.path.join(MODELS_DIR, "movies_lookup.pkl"), "rb") as f:
    movies_df = pickle.load(f)


# Load other saved objects if needed
with open(os.path.join(MODELS_DIR, "global_mean_rating.pkl"), "rb") as f:
    global_mean = pickle.load(f)


def get_recommendations(user_id, top_n=10):
    """
    Generate Top-N movie recommendations for a user.
    """

    # Get all movie IDs
    all_movie_ids = movies_df["movieId"].unique()

    predictions = []

    for movie_id in all_movie_ids:
        prediction = svd.predict(user_id, movie_id)

        predictions.append({"movieId": movie_id, "predicted_rating": prediction.est})

    # Sort from highest predicted rating
    predictions = sorted(predictions, key=lambda x: x["predicted_rating"], reverse=True)

    # Get top movies
    top_predictions = predictions[:top_n]

    results = []

    for item in top_predictions:
        movie = movies_df[movies_df["movieId"] == item["movieId"]]

        if not movie.empty:
            results.append(
                {
                    "movieId": int(item["movieId"]),
                    "title": movie.iloc[0]["title"],
                    "genres": movie.iloc[0].get("genres", ""),
                    "predicted_rating": round(float(item["predicted_rating"]), 2),
                }
            )

    return results
