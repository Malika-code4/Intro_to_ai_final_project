import streamlit as st
import requests

st.set_page_config(page_title="CineMatch", page_icon="🎬")

st.title("🎬 CineMatch")
st.write("Get personalized movie recommendations.")


user_id = st.number_input("Enter your User ID", min_value=1, step=1)


if st.button("Get Recommendations"):
    API_URL = f"http://127.0.0.1:8000/recommendations/{user_id}"

    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()

        recommendations = data["recommendations"]

        st.subheader("🍿 Your Recommendations")

        for movie in recommendations:
            st.write(f"### {movie['title']}")

            st.write(f"🎭 **Genres:** {movie['genres']}")

            st.write(f"⭐ **Predicted Rating:** {movie['predicted_rating']}")

            st.divider()

    else:
        st.error("Could not get recommendations.")
