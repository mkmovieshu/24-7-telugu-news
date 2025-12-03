// static/js/likes.js

import { getCurrentNewsId, setCurrentNews } from "./state.js";
import { sendReaction } from "./api.js";
import { renderReactions } from "./render.js";

const likeBtn = document.getElementById("like-button");
const dislikeBtn = document.getElementById("dislike-button");

export function initLikes() {
  if (!likeBtn || !dislikeBtn) return;

  likeBtn.addEventListener("click", () => handleReaction("like"));
  dislikeBtn.addEventListener("click", () => handleReaction("dislike"));
}

async function handleReaction(type) {
  const newsId = getCurrentNewsId();

  if (!newsId) {
    console.warn("No current news id – reaction skipped");
    return;
  }

  try {
    // backend updated news object return చేస్తుందని assume
    const updatedNews = await sendReaction(newsId, type);
    setCurrentNews(updatedNews);
    renderReactions(updatedNews);

    // యాక్టివ్ బటన్ కలర్ సెట్ చేయడం (css తో) – ఒక్కసారి క్లిక్ చేసినంత వరకే
    if (type === "like") {
      likeBtn.classList.add("active");
      dislikeBtn.classList.remove("active");
    } else {
      dislikeBtn.classList.add("active");
      likeBtn.classList.remove("active");
    }
  } catch (err) {
    console.error("Reaction failed:", err);
  }
}
