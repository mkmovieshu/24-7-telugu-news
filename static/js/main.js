// static/js/main.js
import { fetchNews } from "./api.js";
import { renderNews, setLoading } from "./render.js";
import { initSwipe } from "./swipe.js";
import { initLikes } from "./likes.js";
import { initComments } from "./comments.js";

async function loadInitialNews() {
  setLoading(true);
  const item = await fetchNews(null);
  renderNews(item);
}

async function loadNews(direction) {
  setLoading(true);
  const item = await fetchNews(direction);
  renderNews(item);
}

document.addEventListener("DOMContentLoaded", () => {
  // swipe: పైకి → next, కిందకి → prev
  initSwipe((direction) => {
    loadNews(direction);
  });

  initLikes();
  initComments();
  loadInitialNews();
});
