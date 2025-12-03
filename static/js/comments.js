// static/js/comments.js

import { getCurrentNewsId } from "./state.js";
import { sendComment } from "./api.js";

const commentInput = document.getElementById("comment-input");
const commentButton = document.getElementById("comment-button");

export function initComments() {
  if (!commentInput || !commentButton) return;

  commentButton.addEventListener("click", onSubmit);
}

async function onSubmit() {
  const text = commentInput.value.trim();
  const newsId = getCurrentNewsId();

  if (!text || !newsId) return;

  try {
    await sendComment(newsId, text);
    commentInput.value = "";
    // Future: UI లో “comment saved” toast వంటిది చూపించవచ్చు
  } catch (err) {
    console.error("Failed to send comment:", err);
  }
}
