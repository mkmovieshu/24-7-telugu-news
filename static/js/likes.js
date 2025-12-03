// static/js/likes.js
import { sendReaction } from "./api.js";
import { getCurrentNewsId } from "./render.js";

export function initLikes() {
  const likeBtn = document.getElementById("like-btn");
  const dislikeBtn = document.getElementById("dislike-btn");
  const likeCountEl = document.getElementById("like-count");
  const dislikeCountEl = document.getElementById("dislike-count");

  if (!likeBtn || !dislikeBtn) {
    console.warn("initLikes: buttons missing");
    return;
  }

  likeBtn.addEventListener("click", async () => {
    const newsId = getCurrentNewsId();
    if (!newsId) return;

    const result = await sendReaction(newsId, "like");
    if (result) {
      if (typeof result.likes === "number") {
        likeCountEl.textContent = String(result.likes);
      }
      if (typeof result.dislikes === "number") {
        dislikeCountEl.textContent = String(result.dislikes);
      }
    }
  });

  dislikeBtn.addEventListener("click", async () => {
    const newsId = getCurrentNewsId();
    if (!newsId) return;

    const result = await sendReaction(newsId, "dislike");
    if (result) {
      if (typeof result.likes === "number") {
        likeCountEl.textContent = String(result.likes);
      }
      if (typeof result.dislikes === "number") {
        dislikeCountEl.textContent = String(result.dislikes);
      }
    }
  });
}
