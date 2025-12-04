// static/js/main.js
import { fetchNewsList } from "./api.js";
import { setNewsItems, getCurrentNews } from "./state.js";
import { renderNewsCard, renderInitial } from "./render.js";
import initSwipe from "./swipe.js";
import { initLikes } from "./likes.js";
import { initComments } from "./comments.js";

console.log("main.js starting - module load");

window.addEventListener("DOMContentLoaded", async () => {
  try {
    const raw = await fetchNewsList(50);
    const items = raw.items || [];
    setNewsItems(items);
    renderInitial();

    initSwipe();      // enable swipe handlers
    initLikes();      // bind like buttons
    initComments();   // bind comments
    console.log("App initialized");
  } catch (err) {
    console.error("Failed to init app", err);
    // fallback attempt
    try {
      const r = await fetch("/news?limit=1");
      const data = await r.json();
      setNewsItems(data.items || []);
      renderInitial();
    } catch (e) {
      console.error("Fallback failed", e);
    }
  }
});
