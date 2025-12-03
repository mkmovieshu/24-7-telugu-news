// swipe.js (REPLACE existing file with this)
// Robust vertical swipe handling + comments refresh

import { moveNext, movePrev, getCurrentNews } from "./state.js";
import { renderNewsCard } from "./render.js";
import { loadCommentsForCurrent } from "./comments.js"; // ensures comments refresh after swipe

const cardEl = document.getElementById("news-card");
if (!cardEl) {
  console.warn("swipe.js: #news-card not found");
}

let startX = 0;
let startY = 0;
let lastX = 0;
let lastY = 0;
let tracking = false;
let lockedDirection = null; // "vertical" | "horizontal" | null

const SWIPE_THRESHOLD = 60; // pixels to consider a swipe
const DIRECTION_LOCK_THRESHOLD = 12; // pixels to decide vertical vs horizontal

function onTouchStart(e) {
  tracking = true;
  lockedDirection = null;

  const p = e.touches ? e.touches[0] : e;
  startX = lastX = p.clientX;
  startY = lastY = p.clientY;
}

function onTouchMove(e) {
  if (!tracking) return;
  const p = e.touches ? e.touches[0] : e;
  const dx = p.clientX - startX;
  const dy = p.clientY - startY;

  // decide direction lock
  if (!lockedDirection) {
    if (Math.abs(dy) > DIRECTION_LOCK_THRESHOLD && Math.abs(dy) > Math.abs(dx)) {
      lockedDirection = "vertical";
      // prevent page scroll when we recognized a vertical swipe intention
      // NOTE: this only works if the listener was added with { passive: false }
      try { e.preventDefault(); } catch (err) { /* ignore */ }
    } else if (Math.abs(dx) > DIRECTION_LOCK_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
      lockedDirection = "horizontal";
    }
  } else if (lockedDirection === "vertical") {
    // keep preventing default to avoid page scroll while user swipes
    try { e.preventDefault(); } catch (err) { /* ignore */ }
  }

  lastX = p.clientX;
  lastY = p.clientY;
}

function onTouchEnd(e) {
  if (!tracking) return;
  tracking = false;
  const endX = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientX) || (e.clientX) || lastX;
  const endY = (e.changedTouches && e.changedTouches[0] && e.changedTouches[0].clientY) || (e.clientY) || lastY;

  const dy = startY - endY; // positive => swipe up
  const dx = startX - endX;

  // if we locked to horizontal, ignore
  if (lockedDirection === "horizontal") {
    lockedDirection = null;
    return;
  }

  // only accept vertical swipes larger than threshold and more vertical than horizontal
  if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > SWIPE_THRESHOLD) {
    if (dy > 0) {
      // swipe up -> next
      const news = moveNext();
      renderNewsCard(news, "next");
    } else {
      // swipe down -> prev
      const news = movePrev();
      renderNewsCard(news, "prev");
    }

    // refresh comments for new current item (if comments module present)
    try { loadCommentsForCurrent(); } catch (err) { /* non-fatal */ }
  }

  lockedDirection = null;
}

// Mouse fallback for desktop (click+drag)
let mouseDown = false;
function onMouseDown(e) {
  mouseDown = true;
  startX = e.clientX;
  startY = e.clientY;
  lastX = startX;
  lastY = startY;
}
function onMouseMove(e) {
  if (!mouseDown) return;
  // same logic as touchmove but we won't call preventDefault here
  const dx = e.clientX - startX;
  const dy = e.clientY - startY;
  if (!lockedDirection) {
    if (Math.abs(dy) > DIRECTION_LOCK_THRESHOLD && Math.abs(dy) > Math.abs(dx)) {
      lockedDirection = "vertical";
    } else if (Math.abs(dx) > DIRECTION_LOCK_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
      lockedDirection = "horizontal";
    }
  }
  lastX = e.clientX;
  lastY = e.clientY;
}
function onMouseUp(e) {
  if (!mouseDown) return;
  mouseDown = false;
  onTouchEnd({ changedTouches: [{ clientX: e.clientX, clientY: e.clientY }] });
}

// Attach listeners (touch + mouse)
// IMPORTANT: touchmove must be non-passive to allow preventDefault when we detect vertical intent
try {
  cardEl.addEventListener("touchstart", onTouchStart, { passive: true });
  cardEl.addEventListener("touchmove", onTouchMove, { passive: false });
  cardEl.addEventListener("touchend", onTouchEnd, { passive: true });

  // mouse events
  cardEl.addEventListener("mousedown", onMouseDown);
  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);

  // pointer events for broader support (optional)
  cardEl.addEventListener("pointerdown", (ev) => {
    // if pointer is touch, we've handled in touchstart; still safe
  }, { passive: true });
} catch (err) {
  console.warn("swipe.js attach listeners failed (older browser?)", err);
}
