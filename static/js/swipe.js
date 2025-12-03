// static/js/swipe.js
// Basic vertical swipe detection with a smooth fade animation

window.attachSwipeHandlers = function attachSwipeHandlers(element, handlers) {
  if (!element) return;
  const { onNext, onPrev } = handlers || {};

  let startY = null;
  const threshold = 50; // pixels

  element.addEventListener(
    "touchstart",
    (e) => {
      const touch = e.touches[0];
      startY = touch.clientY;
    },
    { passive: true }
  );

  element.addEventListener(
    "touchend",
    (e) => {
      if (startY === null) return;
      const touch = e.changedTouches[0];
      const deltaY = touch.clientY - startY;

      // small moves ignore
      if (Math.abs(deltaY) < threshold) {
        startY = null;
        return;
      }

      if (deltaY < 0 && typeof onNext === "function") {
        // swipe up -> next news
        animateCard(element, "up");
        onNext();
      } else if (deltaY > 0 && typeof onPrev === "function") {
        // swipe down -> previous news
        animateCard(element, "down");
        onPrev();
      }

      startY = null;
    },
    { passive: true }
  );
};

function animateCard(card, direction) {
  if (!card) return;
  card.classList.remove("swipe-up", "swipe-down");
  void card.offsetWidth; // force reflow
  card.classList.add(direction === "up" ? "swipe-up" : "swipe-down");
}
