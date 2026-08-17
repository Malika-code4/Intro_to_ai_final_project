// ============================================================
// main.js
// ------------------------------------------------------------
// Shared UI helpers used across every page: navbar rendering,
// movie card rendering, the rate/comment modal, and the fake
// "email notification" toast used to simulate the notify-then-
// click-back-to-site flow described in the product requirements.
// ============================================================

// ---------------- Navbar ----------------
function renderNavbar(activePage) {
  const nav = document.getElementById("navbar");
  if (!nav) return;

  const signedIn = AppState.isSignedIn();
  const statusPill = signedIn
    ? `<span class="status-pill signed-in">${AppState.getUserEmail()}</span>`
    : `<span class="status-pill guest">Guest mode</span>`;

  const authLink = signedIn
    ? `<a href="#" id="signOutLink">Sign out</a>`
    : `<a href="signin.html" class="${activePage === 'signin' ? 'active' : ''}">Sign in</a>`;

  nav.innerHTML = `
    <a href="index.html" class="brand">CineMatch</a>
    <div class="nav-links">
      <a href="browse.html" class="${activePage === 'browse' ? 'active' : ''}">Browse</a>
      <a href="recommendations.html" class="${activePage === 'recs' ? 'active' : ''}">Recommendations</a>
      ${authLink}
      ${statusPill}
    </div>
  `;

  const signOutLink = document.getElementById("signOutLink");
  if (signOutLink) {
    signOutLink.addEventListener("click", async (e) => {
      e.preventDefault();
      await API.signOut();
      window.location.href = "index.html";
    });
  }
}

// ---------------- Movie card ----------------
// options: { showMatch: bool, matchLabel: string }
function movieCardHTML(movie, options = {}) {
  const stars = "★".repeat(Math.round(movie.avgRating)) + "☆".repeat(5 - Math.round(movie.avgRating));
  const matchHTML = options.showMatch
    ? `<span class="match-pill">${options.matchLabel || "Recommended for you"}</span>`
    : "";

  return `
    <div class="movie-card" data-movie-id="${movie.id}">
      <div class="movie-poster" style="background:${movie.posterGradient}">
        <span class="poster-badge">${movie.year}</span>
        <span class="poster-title">${movie.title}</span>
      </div>
      <div class="movie-info">
        <div class="genre-year">${movie.genre} • ${movie.year}</div>
        <div class="rating-row">
          <span class="stars">${stars}</span>
          <span>${movie.avgRating.toFixed(1)}</span>
        </div>
        ${matchHTML}
      </div>
    </div>
  `;
}

// Attaches click handlers to every .movie-card inside `container`
// so clicking opens the rate/comment modal for that movie.
function wireMovieCardClicks(container) {
  container.querySelectorAll(".movie-card").forEach((card) => {
    card.addEventListener("click", () => {
      const movieId = Number(card.dataset.movieId);
      openMovieModal(movieId);
    });
  });
}

// ---------------- Modal: rate + comment ----------------
let _modalCurrentMovieId = null;
let _modalSelectedStars = 0;

async function openMovieModal(movieId) {
  const movie = await API.getMovieById(movieId);
  if (!movie) return;

  _modalCurrentMovieId = movieId;
  _modalSelectedStars = AppState.getRatingFor(movieId);

  document.getElementById("modalPosterBg").style.background = movie.posterGradient;
  document.getElementById("modalTitle").textContent = movie.title;
  document.getElementById("modalMeta").textContent = `${movie.genre} • ${movie.year} • ${movie.avgRating.toFixed(1)}★ (${movie.ratingsCount} ratings)`;

  renderStarPicker();
  await renderCommentList(movieId);
  document.getElementById("commentInput").value = "";

  document.getElementById("modalOverlay").classList.add("open");
}

function closeMovieModal() {
  document.getElementById("modalOverlay").classList.remove("open");
  _modalCurrentMovieId = null;
}

function renderStarPicker() {
  const picker = document.getElementById("starPicker");
  picker.innerHTML = "";
  for (let i = 1; i <= 5; i++) {
    const span = document.createElement("span");
    span.className = "star" + (i <= _modalSelectedStars ? " filled" : "");
    span.textContent = "★";
    span.dataset.value = i;
    span.addEventListener("click", async () => {
      _modalSelectedStars = i;
      renderStarPicker();
      await API.submitRating(_modalCurrentMovieId, i);
      showToast("Rating saved", `You rated this ${i} star${i > 1 ? "s" : ""}.`);
    });
    picker.appendChild(span);
  }
}

async function renderCommentList(movieId) {
  const comments = await API.getComments(movieId);
  const list = document.getElementById("commentList");
  if (comments.length === 0) {
    list.innerHTML = `<div class="empty-state" style="padding:20px 0;"><div class="emoji">💬</div>Be the first to comment.</div>`;
    return;
  }
  list.innerHTML = comments.map(c => `
    <div class="comment-item"><span class="comment-user">${c.user}</span>${c.text}</div>
  `).join("");
}

async function submitCommentFromModal() {
  const input = document.getElementById("commentInput");
  const text = input.value.trim();
  if (!text || !_modalCurrentMovieId) return;
  await API.submitComment(_modalCurrentMovieId, text);
  input.value = "";
  await renderCommentList(_modalCurrentMovieId);
  showToast("Comment posted", "Thanks for sharing what you think!");
}

// ---------------- Toast (simulated notification) ----------------
let _toastTimeout = null;
function showToast(title, body, opts = {}) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  document.getElementById("toastTitle").textContent = title;
  document.getElementById("toastBody").textContent = body;

  const actionBtn = document.getElementById("toastAction");
  if (opts.actionLabel && opts.actionHref) {
    actionBtn.style.display = "inline-flex";
    actionBtn.textContent = opts.actionLabel;
    actionBtn.onclick = () => { window.location.href = opts.actionHref; };
  } else {
    actionBtn.style.display = "none";
  }

  toast.classList.add("show");
  clearTimeout(_toastTimeout);
  _toastTimeout = setTimeout(() => toast.classList.remove("show"), 5000);
}

// ---------------- Wire up modal close/comment buttons on load ----------------
document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("modalOverlay");
  if (!overlay) return; // page has no modal (e.g. signin page)

  document.getElementById("modalCloseBtn").addEventListener("click", closeMovieModal);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) closeMovieModal();
  });
  document.getElementById("commentSubmitBtn").addEventListener("click", submitCommentFromModal);
});
