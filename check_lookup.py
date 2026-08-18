import pickle
import os

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

with open(os.path.join(MODELS_DIR, "movies_lookup.pkl"), "rb") as f:
    movies_lookup = pickle.load(f)

print("Type:", type(movies_lookup))
print("\nIndex:", movies_lookup.index)
print("\nColumns:", movies_lookup.columns.tolist())
print("\nHead:\n", movies_lookup.head())
