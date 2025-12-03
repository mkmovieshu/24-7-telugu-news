import { moveNext, movePrev, getCurrentNews } from "./state.js";
import { renderNewsCard } from "./render.js";

const cardEl = document.getElementById("news-card");

let startY = 0;
let endY = 0;
const SWIPE_THRESHOLD = 60;

// Touch start
cardEl.addEventListener("touchstart", (e) => {
  startY = e.touches[0].clientY;
});

// Touch end
cardEl.addEventListener("touchend", (e) => {
  endY = e.changedTouches[0].clientY;
  handleSwipe();
});

// Mouse support (optional)
cardEl.addEventListener("mousedown", (e) => {
  startY = e.clientY;
});

cardEl.addEventListener("mouseup", (e) => {
  endY = e.clientY;
  handleSwipe();
});

function handleSwipe() {
  const diff = startY - endY;

  if (Math.abs(diff) < SWIPE_THRESHOLD) return;

  if (diff > 0) {
    // SWIPE UP → next news
    const news = moveNext();
    renderNewsCard(news, "next");
  } else {
    // SWIPE DOWN → previous news
    const news = movePrev();
    renderNewsCard(news, "prev");
  }
}
