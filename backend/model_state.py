"""
Loads the trained recommendation artifacts (from models/) once at API
startup, plus the Data Engineer's processed training data (from
processed_data/) needed at inference time.

IMPORTANT: these files only exist after your team has actually run
notebooks/data_engineering.ipynb and notebooks/recommendation_developer.ipynb
against the real MovieLens dataset. Until then, this module loads in
"degraded mode" - the app still starts, but recommendation endpoints
return a clear 503 instead of crashing, so the rest of the API (movies,
ratings, comments, auth) stays usable for frontend development in the
meantime.
"""
import os
import sys
import pandas as pd

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "processed_data")

# models/recommender.py isn't an installed package, so add models/ to the
# import path directly rather than requiring a setup.py/pyproject for it.
sys.path.insert(0, MODELS_DIR)

_state = {
    "loaded": False,
    "models": None,
    "train_df": None,
    "recommender": None,
    "error": None,
}


def load():
    """Attempt to load everything. Safe to call more than once."""
    if _state["loaded"] or _state["error"]:
        return _state

    try:
        import recommender  # models/recommender.py

        models = recommender.load_models(model_dir=MODELS_DIR)
        train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "train_data.csv"))

        _state["models"] = models
        _state["train_df"] = train_df
        _state["recommender"] = recommender
        _state["loaded"] = True
    except FileNotFoundError as e:
        _state["error"] = (
            "Trained model artifacts not found in models/ or processed_data/. "
            "Run notebooks/data_engineering.ipynb, then "
            "notebooks/recommendation_developer.ipynb, against the real dataset, "
            f"then copy their output files into these folders. ({e})"
        )
    except Exception as e:
        _state["error"] = f"Failed to load models: {e}"

    return _state


def get_state():
    return _state
