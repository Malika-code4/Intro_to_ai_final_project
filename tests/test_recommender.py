"""
Structural tests for models/recommender.py. Full behavioral testing needs
REAL trained artifacts (models/*.pkl + processed_data/train_data.csv) -
until those exist, this file checks the module imports cleanly and every
function the backend depends on still has the expected name and
parameter order, so a careless edit to recommender.py is caught even
before real data is available to test against.

Run with: pytest tests/test_recommender.py
"""
import os
import sys
import inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "models"))

import recommender


def test_module_imports_cleanly():
    assert recommender is not None


def test_expected_functions_exist():
    expected = [
        "load_models", "content_based_score", "get_top_n_hybrid",
        "get_cluster_recommendations", "cold_start_recommend",
    ]
    for name in expected:
        assert hasattr(recommender, name), f"recommender.py is missing {name}()"


def test_get_top_n_hybrid_signature_matches_backend_usage():
    # backend/routes/recommendations.py calls this positionally as
    # get_top_n_hybrid(user_id, models, train_df, n=n) - if a teammate
    # reorders these params, this test catches it before the API breaks.
    sig = inspect.signature(recommender.get_top_n_hybrid)
    param_names = list(sig.parameters.keys())
    assert param_names[:3] == ["user_id", "models", "train_df"]


def test_cold_start_recommend_signature_matches_backend_usage():
    sig = inspect.signature(recommender.cold_start_recommend)
    param_names = list(sig.parameters.keys())
    assert param_names[:3] == ["new_user_genre_ratings", "models", "train_df"]


def test_load_models_signature_matches_backend_usage():
    # backend/model_state.py calls recommender.load_models(model_dir=MODELS_DIR)
    sig = inspect.signature(recommender.load_models)
    assert "model_dir" in sig.parameters
