// ============================================================
// api.js
// ------------------------------------------------------------
// INTEGRATION LAYER between the front end and the backend
// (see ../../backend/). Every function here calls the real API
// first. If that call fails - e.g. you're opening this file
// directly with no backend running, or models/ isn't populated
// yet - it falls back to the in-browser mock data so the UI
// still works standalone during frontend development.
//
// Change API_BASE_URL below to match wherever backend/main.py is
// actually running.
// ============================================================

const API_BASE_URL = "http://localhost:8000";

// Wraps a fetch() call: on ANY failure (network error, backend not
// running, non-2xx status), logs a warning and falls back to the
// provided mock implementation instead of breaking the page.
async function _withFallback(fetchFn, fallbackFn, label) {
  try {
    const res = await fetchFn();
    if (!res.ok) {
      throw new Error(`${label} responded with ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[api.js] ${label} failed, using mock data instead:`, err.message);
    return fallbackFn();
  }
}

const API = {

  // ---------------- MOVIES ----------------

  async getAllMovies() {
    return _withFallback(
      () => fetch(`${API_BASE_URL}/api/movies`),
      () => MOCK_MOVIES,
      "getAllMovies"
    );
  },

  async searchMovies(query) {
    return _withFallback(
      () => fetch(`${API_BASE_URL}/api/movies/search?q=${encodeURIComponent(query)}`),
      () => {
        const q = query.trim().toLowerCase();
        return MOCK_MOVIES.filter(m =>
          m.title.toLowerCase().includes(q) || m.genre.toLowerCase().includes(q)
        );
      },
      "searchMovies"
    );
  },

  async getMovieById(movieId) {
    return _withFallback(
      () => fetch(`${API_BASE_URL}/api/movies/${movieId}`),
      () => MOCK_MOVIES.find(m => m.id === Number(movieId)) || null,
      "getMovieById"
    );
  },

  // ---------------- RATINGS ----------------

  async submitRating(movieId, stars) {
    // Always record locally too - keeps the "Your recent likes" sidebar
    // and getLikedGenres() working instantly without waiting on a
    // round-trip, and gives us guest behavior for free if the backend
    // call fails.
    AppState.recordRating(movieId, stars);

    return _withFallback(
      () => fetch(`${API_BASE_URL}/api/ratings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movieId,
          stars,
          sessionId: AppState.getSessionId(),
          userId: AppState.getUserId(),
        }),
      }),
      () => ({ success: true }),
      "submitRating"
    );
  },

  // ---------------- COMMENTS ----------------

  async submitComment(movieId, text) {
    const comment = { user: AppState.isGuest() ? "You (guest)" : AppState.getUserEmail(), text };
    AppState.recordComment(movieId, comment);

    const result = await _withFallback(
      () => fetch(`${API_BASE_URL}/api/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          movieId,
          text,
          sessionId: AppState.getSessionId(),
          userId: AppState.getUserId(),
        }),
      }),
      () => ({ success: true }),
      "submitComment"
    );
    return { ...result, comment };
  },

  async getComments(movieId) {
    return _withFallback(
      () => fetch(`${API_BASE_URL}/api/movies/${movieId}/comments`),
      () => {
        const seeded = MOCK_COMMENTS[movieId] || [];
        const sessionOnes = AppState.getCommentsFor(movieId);
        return [...seeded, ...sessionOnes];
      },
      "getComments"
    );
  },

  // ---------------- RECOMMENDATIONS ----------------

  async getTopRecommendations() {
    return _withFallback(
      () => fetch(`${API_BASE_URL}/api/recommendations/top`),
      () => {
        const sorted = [...MOCK_MOVIES].sort((a, b) => {
          const scoreA = a.avgRating * Math.log(a.ratingsCount + 1);
          const scoreB = b.avgRating * Math.log(b.ratingsCount + 1);
          return scoreB - scoreA;
        });
        return sorted.slice(0, 8);
      },
      "getTopRecommendations"
    );
  },

  async getPersonalizedRecommendations() {
    // Send whatever identity + preference signal we have. The backend
    // (backend/routes/recommendations.py) decides which model to use:
    // real SVD+hybrid for a known userId, cluster-based cold-start
    // otherwise. Genres are derived from what the user has rated 4★+
    // so far this session.
    const userId = AppState.getUserId();
    const likedGenres = Array.from(AppState.getLikedGenres());
    const params = new URLSearchParams();
    if (userId) params.set("userId", userId);
    if (likedGenres.length > 0) params.set("genres", likedGenres.join(","));

    return _withFallback(
      () => fetch(`${API_BASE_URL}/api/recommendations/personalized?${params.toString()}`),
      () => {
        const ratedIds = new Set(Object.keys(AppState.getAllRatings()).map(Number));
        if (likedGenres.length === 0) return [];
        const genreSet = new Set(likedGenres);
        return MOCK_MOVIES.filter(m => genreSet.has(m.genre) && !ratedIds.has(m.id))
          .sort((a, b) => b.avgRating - a.avgRating)
          .slice(0, 8);
      },
      "getPersonalizedRecommendations"
    );
  },

  // ---------------- AUTH / ACCOUNT ----------------

  async signInWithEmail(email) {
    const result = await _withFallback(
      () => fetch(`${API_BASE_URL}/api/auth/signin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      }),
      () => ({ success: true, userId: null }),
      "signInWithEmail"
    );
    AppState.setUser(email);
    if (result.userId != null) {
      AppState.setUserId(result.userId);
    }
    return result;
  },

  async signOut() {
    // No real server-side session/token to invalidate with the
    // simplified email-only auth backend/routes/auth.py uses - just
    // clear local state.
    AppState.clearUser();
    return { success: true };
  },

  async subscribeToNotifications() {
    const userId = AppState.getUserId();
    const result = await _withFallback(
      () => fetch(`${API_BASE_URL}/api/notifications/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId }),
      }),
      () => ({ success: true }),
      "subscribeToNotifications"
    );
    AppState.setNotificationsEnabled(true);
    return result;
  }
};
