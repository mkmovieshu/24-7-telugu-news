// static/js/swipe.js

import { fetchNews } from "./api.js";
import { setCurrentNews, setLoading } from "./state.js";
import { renderLoading, renderNews } from "./render.js";

const cardEl = document.getElementById("news-card");

let startY = null;
const SWIPE_THRESHOLD = 50; // pixels

export function initSwipe() {
  if (!cardEl) return;

  cardEl.addEventListener("touchstart", onStart, { passive: true });
  cardEl.addEventListener("touchend", onEnd, { passive: true });

  // mouse support (optional)
  cardEl.addEventListener("mousedown", onMouseDown);
  document.addEventListener("mouseup", onMouseUp);
}

function onStart(e) {
  const touch = e.changedTouches[0];
  startY = touch.clientY;
}

function onEnd(e) {
  if (startY === null) return;
  const touch = e.changedTouches[0];
  const deltaY = touch.clientY - startY;

  if (Math.abs(deltaY) < SWIPE_THRESHOLD) {
    startY = null;
    return;
  }

  if (deltaY < 0) {
    // swipe up → next
    changeNews("next");
  } else {
    // swipe down → previous
    changeNews("prev");
  }

  startY = null;
}

// mouse version
let mouseDownY = null;

function onMouseDown(e) {
  mouseDownY = e.clientY;
}

function onMouseUp(e) {
  if (mouseDownY === null) return;
  const deltaY = e.clientY - mouseDownY;

  if (Math.abs(deltaY) >= SWIPE_THRESHOLD) {
    if (deltaY < 0) {
      changeNews("next");
    } else {
      changeNews("prev");
    }
  }

  mouseDownY = null;
}

async function changeNews(direction) {
  if (!cardEl) return;

  try {
    setLoading(true);
    renderLoading();

    // page-turn animation – card first slides out, తర్వాత కొత్త content తో back in వస్తుంది
    cardEl.classList.remove("card-enter");
    cardEl.classList.add(
      direction === "next" ? "card-exit-up" : "card-exit-down"
    );

    const news = await fetchNews(direction === "next" ? "next" : "prev");
    setCurrentNews(news);

    // చిన్న delay – animation complete అయ్యాక content మారాలి
    setTimeout(() => {
      cardEl.classList.remove("card-exit-up", "card-exit-down");
      renderNews(news);
      cardEl.classList.add(
        direction === "next" ? "card-enter-up" : "card-enter-down"
      );

      // animation finished తర్వాత clean up
      setTimeout(() => {
        cardEl.classList.remove(
          "card-enter",
          "card-enter-up",
          "card-enter-down"
        );
      }, 250);
    }, 180);
  } catch (err) {
    console.error("Swipe changeNews error:", err);
  } finally {
    setLoading(false);
  }
}
