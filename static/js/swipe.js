// static/js/swipe.js
import { moveNext, movePrev } from "./state.js";
const SWIPE_THRESHOLD = 40; // pixels
const DIRECTION_LOCK_THRESHOLD = 12;

let startX = 0, startY = 0;
let locked = false, lockedDirection = null;
let touching = false;

function onTouchStart(ev) {
  touching = true;
  locked = false;
  lockedDirection = null;
  const t = ev.touches ? ev.touches[0] : ev;
  startX = t.clientX;
  startY = t.clientY;
}

function onTouchMove(ev) {
  if (!touching) return;
  const t = ev.touches ? ev.touches[0] : ev;
  const dx = t.clientX - startX;
  const dy = t.clientY - startY;
  if (!locked) {
    if (Math.abs(dx) > DIRECTION_LOCK_THRESHOLD) {
      locked = true;
      lockedDirection = "horizontal";
    } else if (Math.abs(dy) > DIRECTION_LOCK_THRESHOLD) {
      locked = true;
      lockedDirection = "vertical";
    }
  }
  if (locked && lockedDirection === "horizontal") {
    ev.preventDefault();
  }
}

function onTouchEnd(ev) {
  if (!touching) return;
  touching = false;
  const t = (ev.changedTouches && ev.changedTouches[0]) || ev;
  const dx = t.clientX - startX;
  const dy = t.clientY - startY;

  if (lockedDirection === "vertical") {
    // user scrolled vertically; ignore horizontal behavior
    return;
  }
  if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > SWIPE_THRESHOLD) {
    if (dy < 0) {
      // swipe up -> next
      const n = moveNext();
      // render handled externally by app main
    } else {
      const p = movePrev();
    }
  } else if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > SWIPE_THRESHOLD) {
    // optional: horizontal gestures if needed
  }
}

export default function initSwipe() {
  const card = document.getElementById("news-card");
  if (!card) {
    console.warn("initSwipe: no #news-card found");
    return;
  }
  card.addEventListener("touchstart", onTouchStart, { passive: true });
  card.addEventListener("touchmove", onTouchMove, { passive: false });
  card.addEventListener("touchend", onTouchEnd, { passive: true });

  // mouse fallback
  let mouseDown = false;
  card.addEventListener("mousedown", (e) => { mouseDown = true; onTouchStart(e); });
  window.addEventListener("mousemove", (e) => { if (mouseDown) onTouchMove(e); });
  window.addEventListener("mouseup", (e) => { if (mouseDown) { mouseDown = false; onTouchEnd(e); } });
}
