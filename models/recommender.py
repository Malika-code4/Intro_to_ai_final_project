"""
Recommendation Engine — final validated functions.
Depends on: pandas, numpy, scikit-learn, scikit-surprise.
"""
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def load_models(model_dir="./"):
    """Load all trained models and data structures. Call once at app startup."""
    with open(f"{model_dir}/svd_final.pkl", "rb") as f:
        svd = pickle.load(f)
    with open(f"{model_dir}/knn_item_tuned.pkl", "rb") as f:
        knn_item = pickle.load(f)
    with open(f"{model_dir}/kmeans_users.pkl", "rb") as f:
        kmeans_users = pickle.load(f)
    with open(f"{model_dir}/kmeans_movies.pkl", "rb") as f:
        kmeans_movies = pickle.load(f)
    with open(f"{model_dir}/scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open(f"{model_dir}/genre_columns.pkl", "rb") as f:
        genre_columns = pickle.load(f)
    with open(f"{model_dir}/global_mean_rating.pkl", "rb") as f:
        global_mean_rating = pickle.load(f)
    with open(f"{model_dir}/genre_mean_ratings.pkl", "rb") as f:
        genre_mean_ratings = pickle.load(f)

    user_genre_matrix = pd.read_pickle(f"{model_dir}/user_genre_matrix.pkl")
    movie_genre_matrix = pd.read_pickle(f"{model_dir}/movie_genre_matrix.pkl")
    movies_lookup = pd.read_pickle(f"{model_dir}/movies_lookup.pkl")

    return {
        "svd": svd, "knn_item": knn_item, "kmeans_users": kmeans_users,
        "kmeans_movies": kmeans_movies, "scaler": scaler, "genre_columns": genre_columns,
        "user_genre_matrix": user_genre_matrix, "movie_genre_matrix": movie_genre_matrix,
        "movies_lookup": movies_lookup, "global_mean_rating": global_mean_rating,
        "genre_mean_ratings": genre_mean_ratings,
    }


def content_based_score(user_id, candidate_movie_id, user_genre_matrix, movie_genre_matrix, genre_columns):
    """User-centered genre similarity — NOT population z-scored (see methodology
    for why population statistics measure the wrong thing)."""
    if user_id not in user_genre_matrix.index or candidate_movie_id not in movie_genre_matrix.index.get_level_values("movieId"):
        return None
    raw_profile = user_genre_matrix.loc[user_id, genre_columns]
    centered_profile = (raw_profile - raw_profile.mean()).values.reshape(1, -1)
    movie_vector = movie_genre_matrix.xs(candidate_movie_id, level="movieId")[genre_columns].values.reshape(1, -1)
    return cosine_similarity(centered_profile, movie_vector)[0][0] * 5


def get_top_n_hybrid(user_id, models, train_df, n=10, alpha=0.5):
    """Main entry point for EXISTING users. alpha weights CF vs content."""
    svd = models["svd"]
    user_genre_matrix = models["user_genre_matrix"]
    movie_genre_matrix = models["movie_genre_matrix"]
    genre_columns = models["genre_columns"]
    movies_lookup = models["movies_lookup"]

    rated_movies = set(train_df[train_df["userId"] == user_id]["movieId"])
    all_movies = set(movies_lookup["movieId"])
    candidates = list(all_movies - rated_movies)

    cf_scores, content_scores = [], []
    for movie_id in candidates:
        cf_scores.append(svd.predict(user_id, movie_id).est)
        c = content_based_score(user_id, movie_id, user_genre_matrix, movie_genre_matrix, genre_columns)
        content_scores.append(c if c is not None else 0)

    cf_arr, content_arr = np.array(cf_scores), np.array(content_scores)
    cf_norm = (cf_arr - cf_arr.min()) / (cf_arr.max() - cf_arr.min() + 1e-9)
    content_norm = (content_arr - content_arr.min()) / (content_arr.max() - content_arr.min() + 1e-9)
    hybrid = alpha * cf_norm + (1 - alpha) * content_norm

    result = pd.DataFrame({"movieId": candidates, "hybrid_score": hybrid})
    result = result.sort_values("hybrid_score", ascending=False).head(n)
    result = result.merge(movies_lookup[["movieId", "title", "genres"]], on="movieId")
    return result[["movieId", "title", "genres", "hybrid_score"]]


def get_cluster_recommendations(new_user_genre_ratings, models, train_df, n=10):
    """Primary cold-start path — used when the user provides ANY genre input."""
    kmeans_users = models["kmeans_users"]
    kmeans_movies = models["kmeans_movies"]
    scaler = models["scaler"]
    user_genre_matrix = models["user_genre_matrix"]
    movie_genre_matrix = models["movie_genre_matrix"]
    genre_columns = models["genre_columns"]

    genre_means = user_genre_matrix[genre_columns].mean()
    user_vector = genre_means.copy()
    for genre, rating in new_user_genre_ratings.items():
        if genre in user_vector.index:
            user_vector[genre] = rating
    scaled_vector = scaler.transform(pd.DataFrame([user_vector], columns=genre_columns))
    assigned_user_cluster = kmeans_users.predict(scaled_vector)[0]

    stated_genres = [g for g in new_user_genre_ratings.keys() if g in movie_genre_matrix.columns]
    movie_cluster_genre_means = movie_genre_matrix.groupby("cluster")[
        [c for c in movie_genre_matrix.columns if c != "cluster"]
    ].mean()
    relevance_score = movie_cluster_genre_means[stated_genres].mean(axis=1)
    best_movie_cluster = relevance_score.idxmax()

    in_cluster = movie_genre_matrix[movie_genre_matrix["cluster"] == best_movie_cluster]
    has_stated_genre = (in_cluster[stated_genres].sum(axis=1) > 0)
    candidate_movies = in_cluster[has_stated_genre].index.get_level_values("movieId")

    cluster_users = user_genre_matrix[user_genre_matrix["cluster"] == assigned_user_cluster].index
    relevant_ratings = train_df[train_df["userId"].isin(cluster_users) & train_df["movieId"].isin(candidate_movies)]

    movie_stats = (
        relevant_ratings.groupby(["movieId", "title"])
        .agg(mean_rating=("rating", "mean"), num_ratings=("rating", "count"))
        .reset_index()
    )
    reliable = movie_stats[movie_stats["num_ratings"] >= 10]
    top_n = reliable.sort_values("mean_rating", ascending=False).head(n)
    return top_n[["movieId", "title", "mean_rating", "num_ratings"]]


def cold_start_recommend(new_user_genre_ratings, models, train_df, n=10):
    """Entry point: cluster-based if genres given, mean-based fallback if not."""
    if new_user_genre_ratings:
        return get_cluster_recommendations(new_user_genre_ratings, models, train_df, n=n)
    else:
        movie_stats = (
            train_df.groupby(["movieId", "title"])
            .agg(mean_rating=("rating", "mean"), num_ratings=("rating", "count"))
            .reset_index()
        )
        reliable = movie_stats[movie_stats["num_ratings"] >= 20]
        return reliable.sort_values("mean_rating", ascending=False).head(n)