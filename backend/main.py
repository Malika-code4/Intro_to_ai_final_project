from fastapi import FastAPI
from backend.recommendation import get_recommendations

app = FastAPI(title="CineMatch Recommendation API")


@app.get("/")
def home():
    return {"message": "Welcome to CineMatch API"}


@app.get("/recommendations/{user_id}")
def recommendations(user_id: int, top_n: int = 10):

    results = get_recommendations(user_id=user_id, top_n=top_n)

    return {"user_id": user_id, "recommendations": results}
