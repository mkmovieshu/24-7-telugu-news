import { moveNext, movePrev } from "./state.js";
import { renderNewsCard } from "./render.js";

export function initSwipe() {
  const card = document.getElementById("news-card");
  if (!card) return;

  let startY = null;

  card.addEventListener(
    "touchstart",
    (e) => {
      if (e.touches.length === 1) {
        startY = e.touches[0].clientY;
      }
    },
    { passive: true }
  );

  card.addEventListener(
    "touchend",
    (e) => {
      if (startY === null) return;
      const endY = e.changedTouches[0].clientY;
      const diffY = startY - endY;
      const threshold = 40; // minimum swipe distance

      if (Math.abs(diffY) < threshold) {
        startY = null;
        return;
      }

      if (diffY > 0) {
        // swipe up -> next
        const item = moveNext();
        renderNewsCard(item, "next");
      } else {
        // swipe down -> prev
        const item = movePrev();
        renderNewsCard(item, "prev");
      }

      startY = null;
    },
    { passive: true }
  );
}
