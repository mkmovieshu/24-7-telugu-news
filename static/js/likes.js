// static/js/likes.js
// Like / Dislike handling – isolated in this file

(function () {
  const LIKE_BTN_ID = "like-btn";
  const DISLIKE_BTN_ID = "dislike-btn";
  const LIKE_COUNT_ID = "like-count";
  const DISLIKE_COUNT_ID = "dislike-count";

  const STORAGE_KEY = "news-feedback"; // per-browser feedback cache

  function $(id) {
    return document.getElementById(id);
  }

  function getActiveNewsId() {
    const card = document.querySelector("[data-news-id]");
    return card ? card.getAttribute("data-news-id") : null;
  }

  function loadLocalState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      console.warn("Failed to parse local storage feedback", e);
      return {};
    }
  }

  function saveLocalState(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn("Failed to save feedback state", e);
    }
  }

  function setButtonVisuals(action) {
    const likeBtn = $(LIKE_BTN_ID);
    const dislikeBtn = $(DISLIKE_BTN_ID);

    if (!likeBtn || !dislikeBtn) return;

    likeBtn.classList.remove("is-active");
    dislikeBtn.classList.remove("is-active");

    if (action === "like") {
      likeBtn.classList.add("is-active");
    } else if (action === "dislike") {
      dislikeBtn.classList.add("is-active");
    }
  }

  function updateCounts(likes, dislikes) {
    const likeCountEl = $(LIKE_COUNT_ID);
    const dislikeCountEl = $(DISLIKE_COUNT_ID);

    if (likeCountEl) likeCountEl.textContent = likes ?? 0;
    if (dislikeCountEl) dislikeCountEl.textContent = dislikes ?? 0;
  }

  async function sendFeedback(action) {
    const newsId = getActiveNewsId();
    if (!newsId) {
      console.warn("No active news id for feedback");
      return;
    }

    // local cache – avoid double posts from same browser
    const state = loadLocalState();
    const prev = state[newsId];

    // If same action again, ignore
    if (prev === action) {
      return;
    }

    setButtonVisuals(action);

    try {
      const res = await fetch(`/api/news/${newsId}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }), // "like" | "dislike"
      });

      if (!res.ok) {
        throw new Error(`Bad response: ${res.status}`);
      }

      const data = await res.json();
      // backend should return {likes: number, dislikes: number}
      updateCounts(data.likes, data.dislikes);

      state[newsId] = action;
      saveLocalState(state);
    } catch (err) {
      console.error("Failed to send feedback", err);
      // revert visual state if request failed
      state[newsId] = prev || null;
      saveLocalState(state);
      setButtonVisuals(prev || null);
    }
  }

  function restoreStateForCurrentNews() {
    const newsId = getActiveNewsId();
    if (!newsId) return;

    const state = loadLocalState();
    const action = state[newsId] || null;
    setButtonVisuals(action);
  }

  function init() {
    const likeBtn = $(LIKE_BTN_ID);
    const dislikeBtn = $(DISLIKE_BTN_ID);

    if (!likeBtn || !dislikeBtn) {
      console.warn("Like/Dislike buttons not found in DOM");
      return;
    }

    likeBtn.addEventListener("click", () => sendFeedback("like"));
    dislikeBtn.addEventListener("click", () => sendFeedback("dislike"));

    restoreStateForCurrentNews();
  }

  // When page first loads
  document.addEventListener("DOMContentLoaded", init);

  // When you change news via swipe.js, fire a custom event
  // window.dispatchEvent(new CustomEvent("news:changed"))
  // and we’ll re-apply like/dislike state for that news.
  window.addEventListener("news:changed", restoreStateForCurrentNews);
})();
