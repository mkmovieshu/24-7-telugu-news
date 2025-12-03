import { fetchNewsList } from "./api.js";
import { setNewsItems, getCurrentNews } from "./state.js";
import { renderNewsCard } from "./render.js";
import { initSwipe } from "./swipe.js";
import { initLikes } from "./likes.js";
import { initComments } from "./comments.js";

window.addEventListener("DOMContentLoaded", async () => {
  try {
    const items = await fetchNewsList();
    setNewsItems(items);
    const current = getCurrentNews();
    renderNewsCard(current, "initial");

    initSwipe();
    initLikes();
    initComments();
  } catch (err) {
    console.error("Failed to init app", err);
  }
});
