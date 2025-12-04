// static/js/comments.js
import { postComment } from "./api.js";

export function initComments() {
  const send = document.getElementById("comment-send");
  const input = document.getElementById("comment-input");
  if (!send || !input) return;
  send.addEventListener("click", async () => {
    const id = document.getElementById("news-card").dataset.id;
    if (!id) return alert("No news selected");
    const text = input.value.trim();
    if (!text) return;
    try {
      const res = await postComment(id, text);
      if (res && res.ok) {
        alert("Comment posted");
        input.value = "";
      }
    } catch (e) {
      console.error("comment error", e);
      alert("Failed to send comment");
    }
  });
}
