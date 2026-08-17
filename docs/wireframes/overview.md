# Wireframes — CineMatch

This folder contains quick wireframes and notes for the Streamlit version of CineMatch.

Sections:

- Landing / Browse: search bar, three-column grid of movie cards with poster, title, genre, rating control and comment input.
- Sidebar: sign-in info, notification toggle, quick visualizations (genre distribution, rating histogram).
- Recommendations: personalized list generated from user's high ratings and positive comments.

Simple layout sketch (ASCII):

[SIDEBAR] | [ MAIN — Search + Grid ]
          | [ Personalized recommendations ]

Notes:
- Each movie card exposes a compact rating selector and a small comment input.
- Prefer streamlit forms to batch submit per movie to avoid widget collisions.
- Keep notification opt-in in the sidebar (not required to sign in).
