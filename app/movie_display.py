import streamlit as st
from typing import List, Dict, Any
from app.api import submit_rating, submit_comment


def _poster_html(movie: Dict[str, Any]) -> str:
    """Renders a colorful gradient 'poster' with the title overlaid.
    Pure CSS/HTML, no network calls -> always works offline, unlike an
    external placeholder-image service.
    """
    gradient = movie.get("posterGradient", "linear-gradient(160deg,#7f5aff,#3ec6ff)")
    return f"""
    <div style="
        background:{gradient};
        border-radius:12px;
        height:220px;
        display:flex;
        align-items:flex-end;
        padding:12px;
        margin-bottom:8px;
        position:relative;
        overflow:hidden;
    ">
      <div style="
          position:absolute; inset:0;
          background:linear-gradient(to top, rgba(0,0,0,0.55), transparent 60%);
      "></div>
      <span style="
          position:relative; z-index:1; color:white; font-weight:800;
          font-size:1.05rem; text-shadow:0 2px 6px rgba(0,0,0,0.4);
      ">{movie['title']}</span>
    </div>
    """


def show_movie_card(m: Dict[str, Any], session_id: str):
    """Renders one movie card: poster, rating selector, comment box.
    Directly calls submit_rating / submit_comment on button click rather
    than returning a value up the call stack, since callers looping over
    many cards (e.g. show_movie_grid) have no good way to receive a
    per-card return value from Streamlit's rerun model.
    """
    st.markdown(_poster_html(m), unsafe_allow_html=True)
    st.markdown(f"**{m['title']}** ({m['year']})")
    st.caption(f"{m['genre']} • {m['ratingsCount']} ratings • avg {m['avgRating']}")

    rating_key = f"rating_{session_id}_{m['id']}"
    # index=None means no star is pre-selected, so clicking "Submit"
    # without deliberately choosing a rating does nothing instead of
    # silently submitting a default 1-star rating.
    rating = st.select_slider(
        "Your rating", options=[1, 2, 3, 4, 5], value=None, key=rating_key
    )

    comment_key = f"comment_{session_id}_{m['id']}"
    comment = st.text_area("Leave a comment", key=comment_key, help="Optional")

    if st.button("Submit", key=f"submit_{session_id}_{m['id']}"):
        if rating is None and not comment:
            st.warning("Pick a rating or write a comment first.")
        else:
            if rating is not None:
                submit_rating(session_id, m["id"], rating)
            if comment:
                submit_comment(session_id, m["id"], comment)
            st.success(f"Saved for {m['title']}")


def show_movie_grid(movies: List[Dict[str, Any]], session_id: str, columns: int = 3):
    cols = st.columns(columns)
    for i, m in enumerate(movies):
        with cols[i % columns]:
            show_movie_card(m, session_id)
