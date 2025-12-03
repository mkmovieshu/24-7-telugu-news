import { getCurrentNews } from "./state.js";
import { fetchComments, sendComment } from "./api.js";

const listEl = document.getElementById("comments-list");
const inputEl = document.getElementById("comment-text");
const saveBtn = document.getElementById("save-comment-btn");

function renderComments(items) {
  if (!listEl) return;
  listEl.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.className = "comment-empty";
    li.textContent = "ఇంకా కామెంట్లు లేవు.";
    listEl.appendChild(li);
    return;
  }
  for (const c of items) {
    const li = document.createElement("li");
    li.className = "comment-item";
    li.textContent = c.text || "";
    listEl.appendChild(li);
  }
}

async function loadCommentsForCurrent() {
  const item = getCurrentNews();
  if (!item || !item.id) {
    renderComments([]);
    return;
  }
  try {
    const items = await fetchComments(item.id);
    renderComments(items);
  } catch (err) {
    console.error("Failed to load comments", err);
  }
}

export function initComments() {
  if (!inputEl || !saveBtn) return;

  saveBtn.addEventListener("click", async () => {
    const text = (inputEl.value || "").trim();
    if (!text) return;
    const item = getCurrentNews();
    if (!item || !item.id) return;

    try {
      await sendComment(item.id, text);
      inputEl.value = "";
      await loadCommentsForCurrent();
    } catch (err) {
      console.error("Failed to save comment", err);
    }
  });

  // మొదటి వార్తకు comments load చెయ్యాలి
  loadCommentsForCurrent();
}

// external – swipe చేస్తే కొత్త వార్తకి comments refresh కావాలి
export { loadCommentsForCurrent };
