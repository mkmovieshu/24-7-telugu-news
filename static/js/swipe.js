// /static/js/swipe.js
// Improved, robust vertical swipe handler for Next / Prev
// Replaces earlier swipe code. Works on mobile touch & mouse.
// Requires exported functions from ./state.js and ./render.js:
//   moveNext(), movePrev(), getCurrentNews() (state.js)
//   renderNewsCard(item, direction) (render.js)

import { moveNext, movePrev } from "./state.js";
import { renderNewsCard } from "./render.js";

(function () {
  // wait for DOM to be ready (module might run before DOM in some setups)
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  function init() {
    const card = document.getElementById("news-card");
    if (!card) {
      // nothing to attach to — fail silently but log for debugging
      console.warn("swipe.js: #news-card not found, swipe disabled");
      return;
    }

    let startX = 0,
      startY = 0,
      lastX = 0,
      lastY = 0;
    let tracking = false;
    let lockedDirection = null;
    const DIRECTION_LOCK_THRESHOLD = 10; // px before we lock
    const SWIPE_THRESHOLD = 60; // px required to count as a swipe

    function getPoint(e) {
      return (e.touches && e.touches[0]) || e;
    }

    function onStart(e) {
      tracking = true;
      lockedDirection = null;
      const p = getPoint(e);
      startX = lastX = p.clientX;
      startY = lastY = p.clientY;
    }

    function onMove(e) {
      if (!tracking) return;
      const p = getPoint(e);
      const dx = p.clientX - startX;
      const dy = p.clientY - startY;

      // decide direction lock
      if (!lockedDirection) {
        if (Math.abs(dy) > DIRECTION_LOCK_THRESHOLD && Math.abs(dy) > Math.abs(dx)) {
          lockedDirection = "vertical";
          // prevent browser scroll while we handle vertical swipe
          try { e.preventDefault(); } catch (_) {}
        } else if (Math.abs(dx) > DIRECTION_LOCK_THRESHOLD && Math.abs(dx) > Math.abs(dy)) {
          lockedDirection = "horizontal";
        }
      } else if (lockedDirection === "vertical") {
        // while vertical locked, prevent default scrolling on touchmove
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
      const dx = startX - endX;
      const dy = startY - endY;

      // if user performed a horizontal gesture we ignore here
      if (lockedDirection === "horizontal") { lockedDirection = null; return; }

      // check large enough vertical swipe
      if (Math.abs(dy) > Math.abs(dx) && Math.abs(dy) > SWIPE_THRESHOLD) {
        if (dy > 0) {
          // swipe up -> next
          const item = moveNext();
          renderNewsCard(item, "next");
        } else {
          // swipe down -> prev
          const item = movePrev();
          renderNewsCard(item, "prev");
        }
      }

      lockedDirection = null;
    }

    // Attach listeners
    // touch events (mobile)
    card.addEventListener("touchstart", onStart, { passive: true });
    card.addEventListener("touchmove", onMove, { passive: false }); // passive:false so we can preventDefault()
    card.addEventListener("touchend", onEnd, { passive: true });
    card.addEventListener("touchcancel", () => { tracking = false; lockedDirection = null; }, { passive: true });

    // mouse fallback for desktop testing
    let mouseDown = false;
    card.addEventListener("mousedown", function (e) { mouseDown = true; onStart(e); });
    window.addEventListener("mousemove", function (e) { if (mouseDown) onMove(e); });
    window.addEventListener("mouseup", function (e) { if (mouseDown) { mouseDown = false; onEnd(e); } });

    // expose debug helpers on window (optional)
    try {
      window._swipeDebug = {
        simulateNext: () => { const it = moveNext(); renderNewsCard(it, "next"); },
        simulatePrev: () => { const it = movePrev(); renderNewsCard(it, "prev"); }
      };
    } catch (_) {}
  }
})();
