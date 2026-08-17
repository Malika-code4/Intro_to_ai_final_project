import os
import json
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from sklearn.metrics import mean_squared_error, mean_absolute_error, confusion_matrix, ConfusionMatrixDisplay
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Reader, Dataset
import pickle
import scipy.sparse as sp

# Load the data
data_path = 'data.csv'
data = pd.read_csv(data_path)

# Define the reader
reader = Reader(rating_scale=(1, 5))

# Create the dataset
dataset = Dataset.load_from_df(data[['user_id', 'item_id', 'rating']], reader)

# Train the model
model = SVD(n_factors=50, n_epochs=20, verbose=True)

# Make predictions
predictions = model.predict(dataset)

# Evaluate the model
rmse = mean_squared_error(predictions, dataset)
mae = mean_absolute_error(predictions, dataset)

print(f"RMSE: {rmse}")
print(f"MAE: {mae}")

def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

def mae(y_true, y_pred):
    return mean_absolute_error(y_true, y_pred)

def precision_recall_at_k(predictions, k=10, threshold=3.5):
    user_est_true = defaultdict(list)
    for uid, _, true_r, est, _ in predictions:
        user_est_true[uid].append((est, true_r))

    precisions = []
    recalls = []

    for uid, user_ratings in user_est_true.items():
        user_ratings.sort(key=lambda x: x[0], reverse=True)
        top_k = user_ratings[:k]

        n_rel = sum((true_r >= threshold) for (_, true_r) in user_ratings)
        n_rec = sum((true_r >= threshold) for (_, true_r) in top_k)

        precisions.append(n_rec / k if k > 0 else 0)
        recalls.append(n_rec / n_rel if n_rel > 0 else 0)

    return np.mean(precisions), np.mean(recalls)

def evaluate_surprise_model(predictions, name="Model"):
    y_true = [p.r for p in predictions]
    y_pred = [p.est for p in predictions]
    rmse_val = rmse(y_true, y_pred)
    mae_val = mae(y_true, y_pred)
    p_at_10, r_at_10 = precision_recall_at_k(predictions, k=10)

    print(f"{name} Results")
    print(f"RMSE: {rmse_val:.4f}")
    print(f"MAE:  {mae_val:.4f}")
    print(f"Precision@10: {p_at_10:.4f}")
    print(f"Recall@10:    {r_at_10:.4f}")
    print("-" * 20)

    return {"RMSE": rmse_val, "MAE": mae_val, "P@10": p_at_10, "R@10": r_at_10}

# Save the model
model_path = "./model.pkl"
model.save(model_path)

# Create directories for plots and processed data
os.makedirs("./plots", exist_ok=True)
output_dir = "../processed_data"

train_df = pd.read_csv(f"{output_dir}/train_data.csv")
val_df = pd.read_csv(f"{output_dir}/val_data.csv")
test_df = pd.read_csv(f"{output_dir}/test_data.csv")

movies_df = pd.read_csv("../data/Movie_lens_2024/movies.csv")

user_item_matrix = sp.load_npz(f"{output_dir}/user_item_matrix.npz")

with open(f"{output_dir}/user2idx.pkl", "rb") as f:
    user2idx = pickle.load(f)

with open(f"{output_dir}/movie2idx.pkl", "rb") as f:
    movie2idx = pickle.load(f)

global_mean = train_df["rating"].mean()
print("Evaluating K-Means Baseline...")

svd_reducer = TruncatedSVD(n_components=50, random_state=42)
user_embed = svd_reducer.fit_transform(user_item_matrix)

kmeans = KMeans(n_clusters=20, random_state=42, n_init=10)
user_clusters = kmeans.fit_predict(user_embed)

cluster_means = {}
for cluster_id in range(kmeans.n_clusters):
    idx = np.where(user_clusters == cluster_id)[0]
    cluster_matrix = user_item_matrix[idx]
    cluster_avg = np.array(cluster_matrix.mean(axis=0)).flatten()
    cluster_means[cluster_id] = cluster_avg

km_preds = []
for _, row in test_df.iterrows():
    uid = row["userId"]
    mid = row["movieId"]
    if uid in user2idx and mid in movie2idx:
        user_idx = user2idx[uid]
        movie_idx = movie2idx[mid]
        cluster_id = kmeans.predict(user_embed[user_idx].reshape(1, -1))[0]
        km_preds.append(cluster_means[cluster_id][movie_idx])
    else:
        km_preds.append(global_mean)

print(f"K-Means RMSE: {rmse(test_df['rating'].values, km_preds):.4f}")
print(f"K-Means MAE:  {mae(test_df['rating'].values, km_preds):.4f}")

class PopularityRecommender:
    def __init__(self, train_df, min_votes=5):
        movie_stats = train_df.groupby("movieId")["rating"].agg(["mean", "count"]).reset_index()
        movie_stats.columns = ["movieId", "avg_rating", "vote_count"]
        movie_stats = movie_stats[movie_stats["vote_count"] >= min_votes]
        movie_stats["popularity"] = movie_stats["avg_rating"] * np.log(movie_stats["vote_count"] + 1)
        movie_stats = movie_stats.sort_values("popularity", ascending=False)
        self.popularity_scores = movie_stats

    def recommend(self, user_id, k=10):
        top_movies = self.popularity_scores.head(k)[["movieId", "popularity"]]
        return list(zip(top_movies["movieId"].tolist(), top_movies["popularity"].tolist()))

pop_model = PopularityRecommender(train_df, min_votes=10)
print("POPULARITY BASELINE TRAINED")
print(f"Movies with >= 10 votes: {len(pop_model.popularity_scores):,}")
print("Top 10 Most Popular Movies:")
for i, (movie_id, score) in enumerate(pop_model.recommend(1, 10), 1):
    title = movies_df[movies_df["movieId"] == movie_id]["title"].values
    title = title[0] if len(title) > 0 else f"Movie {movie_id}"
    print(f"{i:2d}. {title[:50]:<50} (Score: {score:.2f})")

