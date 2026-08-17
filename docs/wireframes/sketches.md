# Sketches

Quick component sketches and placement ideas.

- Header: app logo + global nav
- Sidebar: session id + notify toggle + small charts
- Main: search box, grid of posters (3 columns), each card has:
  - Poster image (placeholder in mock)
  - Title, genre, year
  - Rating selector (1-5)
  - Comment text input and submit button

Interaction notes:
- After signing in, redirect to browse page (`?sid=...`).
- When user rates >=4 or posts a positive comment (contains "love", "great", "best"), record as positive signal.
- Recommendations page shows "Because you liked [genre]" matches.
