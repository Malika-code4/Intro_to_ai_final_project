import streamlit as st
import pandas as pd
import altair as alt
from typing import List, Dict, Any


def show_genre_distribution(movies: List[Dict[str, Any]]):
    if not movies:
        st.caption("No movie data to chart yet.")
        return
    df = pd.DataFrame(movies)
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('count()', title='Count'),
        y=alt.Y('genre', sort='-x')
    ).properties(height=240)
    st.altair_chart(chart, use_container_width=True)


def show_rating_histogram(movies: List[Dict[str, Any]]):
    if not movies:
        st.caption("No movie data to chart yet.")
        return
    df = pd.DataFrame(movies)
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('avgRating:Q', bin=alt.Bin(maxbins=10)),
        y='count()'
    ).properties(height=180)
    st.altair_chart(chart, use_container_width=True)
