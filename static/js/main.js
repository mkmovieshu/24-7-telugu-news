// main.js
import { loadNews } from "./api.js";
import { next, prev } from "./state.js";
import { showLoading, showError, renderCurrent } from "./render.js";
import { attachSwipe } from "./swipe.js";
import { attachFeedbackHandlers } from "./feedback.js";

const root = document.getElementById("news-root");

async function init() {
  showLoading();
  try {
    await loadNews();
    renderCurrent("up");
  } catch (err) {
    console.error(err);
    showError("న్యూస్ లోడ్ కాలేదు. రీలోడ్ చేసి ప్రయత్నించండి.");
    return;
  }

  attachFeedbackHandlers();
  attachSwipe(root, {
    onSwipeUp: () => {
      if (next()) renderCurrent("up");
    },
    onSwipeDown: () => {
      if (prev()) renderCurrent("down");
    }
  });
}

init();
