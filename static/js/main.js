import { fetchNewsList } from "./api.js";
import { setNewsItems, getCurrentNews } from "./state.js";
import { renderNewsCard } from "./render.js";
import { initSwipe } from "./swipe.js";
import { initLikes } from "./likes.js";
import { initComments } from "./comments.js";

console.log("main.js starting — module load");

window.addEventListener("error", (ev) => {
  console.error("Global error caught:", ev.error || ev.message || ev);
});

window.addEventListener("unhandledrejection", (ev) => {
  console.error("Unhandled promise rejection:", ev.reason);
});

window.addEventListener("DOMContentLoaded", async () => {
  try {
    console.log("DOMContentLoaded — initializing app");
    const items = await fetchNewsList();
    console.log("Fetched news count:", Array.isArray(items) ? items.length : "not-array");
    setNewsItems(items);
    const current = getCurrentNews();
    renderNewsCard(current, "initial");

    initSwipe();
    initLikes();
    initComments();
    console.log("App initialized");
  } catch (err) {
    console.error("Failed to init app", err);
    // In case of error, attempt a defensive fallback render (first item if available)
    try {
      const raw = await fetch("/news");
      if (raw.ok) {
        const data = await raw.json();
        const first = data.items && data.items[0];
        if (first) {
          // try to write into DOM directly
          const t = document.getElementById("news-title");
          const s = document.getElementById("news-summary");
          if (t) t.textContent = first.title || "టైటిల్ లేదు";
          if (s) s.textContent = first.summary || first.raw_summary || "";
        }
      }
    } catch (e) {
      console.error("Fallback failed", e);
    }
  }
});
