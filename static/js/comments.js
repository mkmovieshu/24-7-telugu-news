// comments.js
// functions to load & render comments for the current news card.

import { fetchComments, sendComment } from "./api.js";

function createCommentNode(c) {
  const li = document.createElement("li");
  li.className = "comment-item";
  const when = new Date(c.created_at).toLocaleString();
  li.textContent = `${c.text} — ${when}`;
  return li;
}

export async function loadCommentsForNews(newsId, targetListEl) {
  // returns items array
  console.log("[comments] loadCommentsForNews", newsId);
  if (!newsId) return [];
  try {
    const items = await fetchComments(newsId);
    targetListEl.innerHTML = "";
    if (!items || items.length === 0) {
      targetListEl.innerHTML = `<li class="comment-empty">కానీ కామెంట్స్ ఎలాంటి లేవు</li>`;
      return items;
    }
    items.forEach(c => targetListEl.appendChild(createCommentNode(c)));
    return items;
  } catch (err) {
    console.error("[comments] loadCommentsForNews error", err);
    targetListEl.innerHTML = `<li class="comment-empty">కామెంట్లు లోడ్ చేయలేకపోయాం</li>`;
    return [];
  }
}

export async function saveCommentForNews(newsId, text) {
  console.log("[comments] saveCommentForNews", newsId, text);
  if (!text || !text.trim()) throw new Error("Empty comment");
  return await sendComment(newsId, text.trim());
}

// named export used by other modules
export { createCommentNode as _createCommentNode };
