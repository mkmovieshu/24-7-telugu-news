// static/js/comments.js
// Handles comment UI behaviour and exports expected functions
import { loadCommentsForCurrent, postComment } from "./api.js";
import { getItemId } from "./state.js";

const COMMENTS_SELECTOR = ".comments-section";

/**
 * load and render comments for given newsId into the card's comments list
 * returns comments array
 */
export async function loadComments(newsId, container) {
  try {
    const items = await loadCommentsForCurrent(newsId);
    renderCommentsList(container, items);
    return items;
  } catch (err) {
    console.error("loadComments error", err);
    renderCommentsList(container, []);
    return [];
  }
}

// compatibility name used by some modules
export const loadCommentsForCurrentNews = loadComments;
export const loadCommentsForCurrent = loadComments;

/**
 * post a comment (wrap API) then re-render
 */
export async function submitComment(newsId, text, container) {
  if (!text || !text.trim()) return null;
  try {
    await postComment(newsId, text);
    // reload comments (simple approach)
    const items = await loadComments(newsId, container);
    return items;
  } catch (err) {
    console.error("submitComment error", err);
    throw err;
  }
}

// UI helpers
function renderCommentsList(container, items) {
  // expects container to be element that holds .comments-list
  const list = container.querySelector(".comments-list");
  if (!list) return;
  if (!items || items.length === 0) {
    list.innerHTML = `<div class="comment-empty">No comments yet</div>`;
    return;
  }
  list.innerHTML = items
    .map((c) => `<div class="comment-item">${escapeHtml(c.text || "")}</div>`)
    .join("");
}

function escapeHtml(s) {
  return (s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

/* initComments — used by main.js to wire up event handlers */
export function initComments() {
  document.addEventListener("click", async (e) => {
    // open comments toggle
    const btn = e.target.closest("[data-action='toggle-comments']");
    if (btn) {
      const card = btn.closest(".card");
      if (!card) return;
      const newsId = card.dataset.id || btn.datasetNewsId || btn.dataset.newsId;
      const section = card.querySelector("[data-comments]");
      if (!section) return;
      section.classList.toggle("visible");
      if (section.classList.contains("visible")) {
        // load comments
        await loadComments(newsId, section);
      }
      return;
    }

    // submit comment button
    const send = e.target.closest("[data-action='submit-comment']");
    if (send) {
      const card = send.closest(".card");
      if (!card) return;
      const newsId = card.dataset.id;
      const section = card.querySelector("[data-comments]");
      const input = section && section.querySelector(".comment-input");
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;
      try {
        await submitComment(newsId, text, section);
        input.value = "";
      } catch (_) {
        // optionally show error
      }
      return;
    }
  });
}
