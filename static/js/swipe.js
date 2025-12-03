// static/js/swipe.js

// Simple vertical swipe detector
const SWIPE_THRESHOLD = 50; // px

export function initSwipe(onSwipe) {
  const card = document.getElementById("news-card");
  if (!card) {
    console.warn("initSwipe: #news-card not found");
    return;
  }

  let startY = null;
  let isTouch = false;

  card.addEventListener("touchstart", (e) => {
    isTouch = true;
    startY = e.touches[0].clientY;
  });

  card.addEventListener("touchend", (e) => {
    if (!isTouch || startY === null) return;
    const endY = e.changedTouches[0].clientY;
    handleSwipe(startY, endY, onSwipe);
    startY = null;
  });

  // Optional: mouse swipe support (desktop)
  card.addEventListener("mousedown", (e) => {
    isTouch = false;
    startY = e.clientY;
  });

  card.addEventListener("mouseup", (e) => {
    if (startY === null) return;
    const endY = e.clientY;
    handleSwipe(startY, endY, onSwipe);
    startY = null;
  });
}

function handleSwipe(startY, endY, onSwipe) {
  const diffY = startY - endY;

  if (Math.abs(diffY) < SWIPE_THRESHOLD) return;

  if (diffY > 0) {
    // swipe UP → next
    onSwipe("next");
  } else {
    // swipe DOWN → previous
    onSwipe("prev");
  }
}
