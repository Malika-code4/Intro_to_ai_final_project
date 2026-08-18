from backend import model_state

state = model_state.get_state()
if not state["loaded"]:
    model_state.load()
    state = model_state.get_state()

recommender = state["recommender"]
models = state["models"]
train_df = state["train_df"]

sample_user = train_df["userId"].iloc[0]

result = recommender.get_top_n_hybrid(sample_user, models, train_df, n=3)
print("Columns:", result.columns.tolist())
print(result.head())
