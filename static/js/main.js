// static/js/main.js

import { fetchNews } from "./api.js";
import { setCurrentNews, setLoading } from "./state.js";
import { renderLoading, renderNews, renderError } from "./render.js";
import { initSwipe } from "./swipe.js";
import { initLikes } from "./likes.js";
import { initComments } from "./comments.js";

window.addEventListener("DOMContentLoaded", async () => {
  setLoading(true);
  renderLoading();

  try {
    const news = await fetchNews("current");
    setCurrentNews(news);
    renderNews(news);
  } catch (err) {
    console.error(err);
    renderError("సర్వర్ నుండి న్యూస్ రాలేదు.");
  } finally {
    setLoading(false);
  }

  initSwipe();
  initLikes();
  initComments();
});
