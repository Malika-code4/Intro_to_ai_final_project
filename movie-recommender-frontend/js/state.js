// ============================================================
// state.js
// ------------------------------------------------------------
// FRONT-END-ONLY session state manager.
// - Guests: everything lives in sessionStorage -> wiped when the
//   browser tab/window is closed (per product requirement: guests
//   lose their activity once they leave).
// - Signed-in users: same storage mechanism for now (front end
//   only, no real backend yet), but this is the ONE place the
//   backend team needs to touch to instead persist this server-side
//   and attach it to a real account.
// ============================================================

const AppState = (function () {
  const RATINGS_KEY = "mre_ratings";      // { movieId: stars }
  const COMMENTS_KEY = "mre_comments";    // { movieId: [ {user, text}, ... ] }
  const USER_KEY = "mre_user_email";      // string | null
  const USER_ID_KEY = "mre_user_id";      // number | null - backend's users.id
  const SESSION_ID_KEY = "mre_session_id"; // string - stable per guest session
  const NOTIF_KEY = "mre_notifications";  // "true" | "false"

  function _get(key, fallback) {
    const raw = sessionStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  }
  function _set(key, value) {
    sessionStorage.setItem(key, JSON.stringify(value));
  }

  function _generateSessionId() {
    if (window.crypto && window.crypto.randomUUID) {
      return window.crypto.randomUUID();
    }
    // Fallback for older browsers without crypto.randomUUID
    return "guest-" + Date.now() + "-" + Math.random().toString(36).slice(2);
  }

  return {
    // ---- session/user identity (needed so api.js can tell the backend
    // whose rating/comment this is - see backend/database.py's
    // session_id/user_id columns) ----
    getSessionId() {
      let id = _get(SESSION_ID_KEY, null);
      if (!id) {
        id = _generateSessionId();
        _set(SESSION_ID_KEY, id);
      }
      return id;
    },
    setUserId(id) {
      _set(USER_ID_KEY, id);
    },
    getUserId() {
      return _get(USER_ID_KEY, null);
    },
    clearUserId() {
      sessionStorage.removeItem(USER_ID_KEY);
    },

    // ---- ratings ----
    recordRating(movieId, stars) {
      const ratings = _get(RATINGS_KEY, {});
      ratings[movieId] = stars;
      _set(RATINGS_KEY, ratings);
    },
    getAllRatings() {
      return _get(RATINGS_KEY, {});
    },
    getRatingFor(movieId) {
      const ratings = _get(RATINGS_KEY, {});
      return ratings[movieId] || 0;
    },

    // ---- comments ----
    recordComment(movieId, comment) {
      const comments = _get(COMMENTS_KEY, {});
      if (!comments[movieId]) comments[movieId] = [];
      comments[movieId].push(comment);
      _set(COMMENTS_KEY, comments);
    },
    getCommentsFor(movieId) {
      const comments = _get(COMMENTS_KEY, {});
      return comments[movieId] || [];
    },

    // ---- derived: which genres has this user liked (rated 4+) ----
    getLikedGenres() {
      const ratings = _get(RATINGS_KEY, {});
      const liked = new Set();
      Object.entries(ratings).forEach(([movieId, stars]) => {
        if (stars >= 4) {
          const movie = MOCK_MOVIES.find(m => m.id === Number(movieId));
          if (movie) liked.add(movie.genre);
        }
      });
      return liked;
    },

    // ---- derived: full movie objects the user rated highly (4-5 stars),
    // used by recommendations.html's "Your recent likes" sidebar summary.
    // Also counts a movie as "liked" if the user left a positive-sounding
    // comment on it even without a high star rating, per the sketches.md
    // note: "positive comment (contains 'love', 'great', 'best')".
    // Returns: Array<{ movie: Movie, rating: number }>, highest rating first.
    getLikedMovies() {
      const ratings = _get(RATINGS_KEY, {});
      const comments = _get(COMMENTS_KEY, {});
      const positiveWords = ["love", "great", "best", "amazing", "favorite", "loved"];

      const likedIds = new Map(); // movieId -> best rating seen (or 0 if only comment-based)

      Object.entries(ratings).forEach(([movieId, stars]) => {
        if (stars >= 4) likedIds.set(Number(movieId), stars);
      });

      Object.entries(comments).forEach(([movieId, commentList]) => {
        const id = Number(movieId);
        const hasPositiveComment = commentList.some(c =>
          positiveWords.some(w => c.text.toLowerCase().includes(w))
        );
        if (hasPositiveComment && !likedIds.has(id)) {
          likedIds.set(id, 0); // liked via comment, no star rating on record
        }
      });

      const results = [];
      likedIds.forEach((rating, movieId) => {
        const movie = MOCK_MOVIES.find(m => m.id === movieId);
        if (movie) results.push({ movie, rating });
      });

      results.sort((a, b) => b.rating - a.rating);
      return results;
    },

    hasAnyActivity() {
      const ratings = _get(RATINGS_KEY, {});
      const comments = _get(COMMENTS_KEY, {});
      return Object.keys(ratings).length > 0 || Object.keys(comments).length > 0;
    },

    // ---- user / auth ----
    setUser(email) {
      _set(USER_KEY, email);
    },
    clearUser() {
      sessionStorage.removeItem(USER_KEY);
      sessionStorage.removeItem(USER_ID_KEY);
    },
    getUserEmail() {
      return _get(USER_KEY, null);
    },
    isSignedIn() {
      return !!this.getUserEmail();
    },
    isGuest() {
      return !this.isSignedIn();
    },

    // ---- notifications ----
    setNotificationsEnabled(value) {
      _set(NOTIF_KEY, value);
    },
    notificationsEnabled() {
      return _get(NOTIF_KEY, false);
    }
  };
})();
