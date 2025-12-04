// static/js/swipe.js
import { moveNext, movePrev, getCurrentNews } from "./state.js";
import { renderNewsCard } from "./render.js";
import { loadCommentsForCurrent } from "./comments.js";

/**
 * initSwipe()
 * Attach all touch / mouse handlers lazily after DOM is ready.
 * Exports a single function that main.js calls on DOMContentLoaded.
 */

export function initSwipe() {
  const cardEl = document.getElementById("news-card");
  if (!cardEl) {
    console.warn("swipe.initSwipe: #news-card not found – swipe disabled");
    return;
  }

  let startX = 0;
  let startY = 0;
  let lastX = 0;
  let lastY = 0;
  let tracking = false;
  let lockedDirection = null;

  const SWIPE_THRESHOLD = 60; // pixels to consider a swipe
  const DIRECTION_LOCK_THRESHOLD = 12; // pixels to lock axis

  function onStart(e) {
    tracking = true;
    lockedDirection = null;
    const p = (e.touches && e.touches[0]) || e;
    startX = lastX = p.clientX;
    startY = lastY = p.clientY;
  }

  function onMove(e) {
    if (!tracking) return;
    const p = (e.touches && e.touches[0]) || e;
    const dx = p.clientX - startX;
    const dy = p.clientY - startY;

    if (!lockedDirection) {
      if (Math.abs(dy) > DIRECTION_LOCK_THRESHOLD && Math.abs(dy) > Math.abs(dx)) {
        lockedDirection = "vertical";
        try { e.preventDefault(); } catch (_) {}
      } else if (Math.abs(dx) > DIRECTION_LOCK_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
        lockedDirection = "horizontal";
      }
    } else if (lockedDirection === "vertical") {
      try { e.preventDefault(); } catch (_) {}
    }

    lastX = p.clientX;
    lastY = p.clientY;
  }

  function onEnd(e) {
    if (!tracking) return;
    tracking = false;

    const changed = (e.changedTouches && e.changedTouches[0]) || {};
    const endX = changed.clientX || lastX;
    const endY = changed.clientY || lastY;

    const dy = startY - endY;
    const dx = startX - endX;

    // if horizontal swipe locked, ignore
    if (lockedDirection === "horizontal") {
      lockedDirection = null;
      return;
    }

    // small drags ignored
    if (Math.abs(dy) < SWIPE_THRESHOLD) {
      lockedDirection = null;
      return;
    }

    if (dy > 0) {
      // swipe up => next
      const news = moveNext();
      // moveNext() returns the new current item (or null)
      renderNewsCard(news, "next");
    } else {
      // swipe down => previous
      const news = movePrev();
      renderNewsCard(news, "prev");
    }

    // refresh comments for the newly shown news (if comments module present)
    try {
      loadCommentsForCurrent();
    } catch (err) {
      // silent — comments optional
      // console.debug("loadCommentsForCurrent not available:", err);
    }

    lockedDirection = null;
  }

  // Touch events
  cardEl.addEventListener("touchstart", onStart, { passive: true });
  cardEl.addEventListener("touchmove", onMove, { passive: false });
  cardEl.addEventListener("touchend", onEnd, { passive: true });

  // Mouse support (desktop)
  cardEl.addEventListener("mousedown", onStart);
  cardEl.addEventListener("mousemove", onMove);
  cardEl.addEventListener("mouseup", onEnd);

  // For keyboard accessibility: up/down arrows
  cardEl.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      const news = moveNext();
      renderNewsCard(news, "next");
      try { loadCommentsForCurrent(); } catch (_) {}
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      const news = movePrev();
      renderNewsCard(news, "prev");
      try { loadCommentsForCurrent(); } catch (_) {}
    }
  });

  // make card focusable for keyboard arrows
  if (!cardEl.hasAttribute("tabindex")) cardEl.setAttribute("tabindex", "0");
}
