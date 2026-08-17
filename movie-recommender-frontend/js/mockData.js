// ============================================================
// mockData.js
// ------------------------------------------------------------
// FRONT-END ONLY placeholder data.
// This file simulates what the BACKEND / API will eventually
// return. When the backend is ready, delete/ignore this file
// and make sure api.js's functions fetch from real endpoints
// instead of reading from these arrays.
// ============================================================

const MOCK_GENRES = [
  "Action", "Comedy", "Drama", "Romance", "Sci-Fi",
  "Horror", "Animation", "Thriller", "Documentary", "Fantasy"
];

// Colorful gradient palette used to fake "poster art" per movie
// (real posters will come from backend / TMDB-like image URLs later)
const POSTER_GRADIENTS = [
  "linear-gradient(160deg,#ff6b6b,#f9d423)",
  "linear-gradient(160deg,#7f7fd5,#86a8e7,#91eae4)",
  "linear-gradient(160deg,#f857a6,#ff5858)",
  "linear-gradient(160deg,#43cea2,#185a9d)",
  "linear-gradient(160deg,#ffb347,#ffcc33)",
  "linear-gradient(160deg,#a18cd1,#fbc2eb)",
  "linear-gradient(160deg,#ff9a9e,#fecfef)",
  "linear-gradient(160deg,#30cfd0,#330867)",
  "linear-gradient(160deg,#f6d365,#fda085)",
  "linear-gradient(160deg,#84fab0,#8fd3f4)",
  "linear-gradient(160deg,#cc2b5e,#753a88)",
  "linear-gradient(160deg,#00c6ff,#0072ff)"
];

const MOCK_MOVIES = [
  { id: 1,  title: "Nebula Drift",         year: 2021, genre: "Sci-Fi",      avgRating: 4.6, ratingsCount: 812 },
  { id: 2,  title: "Laugh Track",          year: 2019, genre: "Comedy",      avgRating: 4.1, ratingsCount: 530 },
  { id: 3,  title: "Silent Harbor",        year: 2020, genre: "Drama",       avgRating: 4.4, ratingsCount: 950 },
  { id: 4,  title: "Crimson Vow",          year: 2018, genre: "Romance",     avgRating: 3.9, ratingsCount: 410 },
  { id: 5,  title: "Iron Skyline",         year: 2022, genre: "Action",      avgRating: 4.7, ratingsCount: 1320 },
  { id: 6,  title: "The Quiet House",      year: 2017, genre: "Horror",      avgRating: 4.0, ratingsCount: 289 },
  { id: 7,  title: "Paper Lantern Town",   year: 2016, genre: "Animation",   avgRating: 4.5, ratingsCount: 670 },
  { id: 8,  title: "Static Line",         year: 2023, genre: "Thriller",    avgRating: 4.3, ratingsCount: 745 },
  { id: 9,  title: "Wandering Coastline",  year: 2015, genre: "Documentary", avgRating: 4.2, ratingsCount: 198 },
  { id: 10, title: "Ember & Ash",          year: 2021, genre: "Fantasy",     avgRating: 4.6, ratingsCount: 860 },
  { id: 11, title: "Second Sunrise",       year: 2019, genre: "Drama",       avgRating: 3.8, ratingsCount: 320 },
  { id: 12, title: "Neon Alley Cats",      year: 2020, genre: "Comedy",      avgRating: 4.0, ratingsCount: 455 },
  { id: 13, title: "Glass Orchard",        year: 2022, genre: "Romance",     avgRating: 4.3, ratingsCount: 590 },
  { id: 14, title: "Fracture Point",       year: 2018, genre: "Action",      avgRating: 4.4, ratingsCount: 980 },
  { id: 15, title: "Hollow Bell",          year: 2017, genre: "Horror",      avgRating: 3.7, ratingsCount: 210 },
  { id: 16, title: "The Cartographer",     year: 2021, genre: "Fantasy",     avgRating: 4.8, ratingsCount: 1100 },
  { id: 17, title: "Midnight Ferry",       year: 2016, genre: "Thriller",    avgRating: 4.1, ratingsCount: 402 },
  { id: 18, title: "Sun-Bleached",         year: 2023, genre: "Drama",       avgRating: 4.5, ratingsCount: 733 },
  { id: 19, title: "Tin Can Symphony",     year: 2019, genre: "Animation",   avgRating: 4.2, ratingsCount: 511 },
  { id: 20, title: "Undertow",             year: 2020, genre: "Sci-Fi",      avgRating: 4.6, ratingsCount: 890 },
  { id: 21, title: "Rice Paper Moon",      year: 2015, genre: "Romance",     avgRating: 3.9, ratingsCount: 245 },
  { id: 22, title: "Broken Compass",       year: 2022, genre: "Action",      avgRating: 4.0, ratingsCount: 600 },
  { id: 23, title: "The Long Static",      year: 2018, genre: "Documentary", avgRating: 4.3, ratingsCount: 176 },
  { id: 24, title: "Velvet Frequency",     year: 2021, genre: "Comedy",      avgRating: 4.1, ratingsCount: 388 }
];

MOCK_MOVIES.forEach((m, i) => {
  m.posterGradient = POSTER_GRADIENTS[i % POSTER_GRADIENTS.length];
});

const MOCK_COMMENTS = {
  1: [{ user: "reelfan22", text: "Visually stunning, the score alone is worth it." }],
  5: [{ user: "cinequeen", text: "Best action sequences all year." }],
  16: [{ user: "mapnerd", text: "Underrated. The world-building is incredible." }]
};
