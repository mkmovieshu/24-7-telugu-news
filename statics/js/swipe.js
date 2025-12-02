// swipe.js

export function attachSwipe(container, { onSwipeUp, onSwipeDown }) {
  let startY = null;
  let startTime = 0;

  const threshold = 50; // px
  const maxTime = 600; // ms

  function onTouchStart(e) {
    const touch = e.touches[0];
    startY = touch.clientY;
    startTime = Date.now();
  }

  function onTouchEnd(e) {
    if (startY === null) return;
    const touch = e.changedTouches[0];
    const diffY = touch.clientY - startY;
    const dt = Date.now() - startTime;

    if (dt <= maxTime && Math.abs(diffY) > threshold) {
      if (diffY < 0 && typeof onSwipeUp === "function") {
        onSwipeUp();
      } else if (diffY > 0 && typeof onSwipeDown === "function") {
        onSwipeDown();
      }
    }

    startY = null;
  }

  container.addEventListener("touchstart", onTouchStart, { passive: true });
  container.addEventListener("touchend", onTouchEnd, { passive: true });

  // keyboard: up/down arrows
  window.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") {
      onSwipeUp && onSwipeUp();
    } else if (e.key === "ArrowDown") {
      onSwipeDown && onSwipeDown();
    }
  });
}
