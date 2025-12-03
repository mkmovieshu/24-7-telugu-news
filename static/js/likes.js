import { getCurrentNews } from "./state.js";
import { sendReaction } from "./api.js";
import { updateReactions } from "./render.js";

export function initLikes() {
  const likeBtn = document.getElementById("like-btn");
  const dislikeBtn = document.getElementById("dislike-btn");

  async function handle(action) {
    const item = getCurrentNews();
    if (!item || !item.id) return;

    try {
      const res = await sendReaction(item.id, action);
      updateReactions(res.likes, res.dislikes);
    } catch (err) {
      console.error("Reaction failed", err);
    }
  }

  likeBtn?.addEventListener("click", () => handle("like"));
  dislikeBtn?.addEventListener("click", () => handle("dislike"));
}
