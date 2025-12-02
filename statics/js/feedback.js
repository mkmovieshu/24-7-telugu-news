// feedback.js
import {
  getItems,
  getCurrentIndex,
  getItemId,
  getReactions,
  setReaction,
  addComment,
  getComments
} from "./state.js";
import { renderCurrent } from "./render.js";

const root = document.getElementById("news-root");

export function attachFeedbackHandlers() {
  root.addEventListener("click", (e) => {
    const action = e.target.dataset.action;
    if (!action) return;

    if (action === "like" || action === "dislike") {
      handleReaction(action);
    } else if (action === "toggle-comments") {
      toggleComments();
    } else if (action === "submit-comment") {
      submitComment();
    }
  });
}

function getCurrentItemAndId() {
  const items = getItems();
  const idx = getCurrentIndex();
  const item = items[idx];
  const id = getItemId(item, idx);
  return { item, id };
}

function handleReaction(type) {
  const { id } = getCurrentItemAndId();
  setReaction(id, type);

  // UI update
  const card = root.querySelector(".card");
  if (!card) return;
  const likeBtn = card.querySelector('[data-action="like"]');
  const dislikeBtn = card.querySelector('[data-action="dislike"]');
  const rec = getReactions(id);

  likeBtn.querySelector(".count").textContent = rec.like;
  dislikeBtn.querySelector(".count").textContent = rec.dislike;

  likeBtn.classList.toggle("active", rec.my === "like");
  dislikeBtn.classList.toggle("active", rec.my === "dislike");
}

function toggleComments() {
  const card = root.querySelector(".card");
  if (!card) return;
  const section = card.querySelector("[data-comments]");
  if (!section) return;
  const list = section.querySelector(".comments-list");
  const toggleBtn = card.querySelector('[data-action="toggle-comments"]');

  section.classList.toggle("visible");
  if (toggleBtn && list) {
    const { id } = getCurrentItemAndId();
    const count = getComments(id).length;
    toggleBtn.textContent = `కామెంట్స్ (${count})`;
  }
}

function submitComment() {
  const card = root.querySelector(".card");
  if (!card) return;
  const section = card.querySelector("[data-comments]");
  const input = section.querySelector(".comment-input");
  const list = section.querySelector(".comments-list");
  const toggleBtn = card.querySelector('[data-action="toggle-comments"]');

  const text = input.value.trim();
  if (!text) return;

  const { id } = getCurrentItemAndId();
  addComment(id, text);
  input.value = "";

  const comments = getComments(id);
  list.innerHTML = comments
    .map((c) => `<div class="comment-item">${c}</div>`)
    .join("");

  if (toggleBtn) {
    toggleBtn.textContent = `కామెంట్స్ (${comments.length})`;
  }
}
