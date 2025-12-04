// static/js/likes.js
import { postReaction } from "./api.js";
import { updateReactions } from "./render.js";

export function initLikes() {
  const likeBtn = document.getElementById("like-btn");
  const dislikeBtn = document.getElementById("dislike-btn");
  if (!likeBtn || !dislikeBtn) return;

  likeBtn.addEventListener("click", async () => {
    const id = document.getElementById("news-card").dataset.id;
    if (!id) return;
    try {
      const data = await postReaction(id, "like");
      if (data && data.likes !== undefined) updateReactions(data.likes, data.dislikes);
    } catch (e) {
      console.error("like failed", e);
    }
  });

  dislikeBtn.addEventListener("click", async () => {
    const id = document.getElementById("news-card").dataset.id;
    if (!id) return;
    try {
      const data = await postReaction(id, "dislike");
      if (data && data.likes !== undefined) updateReactions(data.likes, data.dislikes);
    } catch (e) {
      console.error("dislike failed", e);
    }
  });
}
