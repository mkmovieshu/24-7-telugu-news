// static/js/swipe.js
// Vertical swipe up => Next news
// Vertical swipe down => Prev news
// Works on touch devices and pointer devices.
// If window.nextNews / window.prevNews functions exist, call them.
// Otherwise try to click "Next"/"Prev" buttons found on the page.

(function () {
  const THRESHOLD = 60; // minimum vertical px for swipe
  const MAX_HORIZONTAL = 100; // max allowed horizontal movement
  const MAX_TIME = 1000; // max ms for gesture

  let startX = 0;
  let startY = 0;
  let startTime = 0;
  let tracking = false;

  function isFormElement(el) {
    if (!el) return false;
    const tag = (el.tagName || "").toLowerCase();
    return tag === "input" || tag === "textarea" || tag === "select" || el.isContentEditable;
  }

  function findButtonByText(text) {
    const buttons = Array.from(document.querySelectorAll("button, a"));
    const lower = text.toLowerCase();
    for (let b of buttons) {
      const t = (b.innerText || b.textContent || "").trim().toLowerCase();
      if (t === lower) return b;
      // sometimes "Next »" or icons: look if startsWith
      if (t.indexOf(lower) === 0) return b;
    }
    return null;
  }

  function triggerNext() {
    if (typeof window.nextNews === "function") {
      window.nextNews();
      return;
    }
    // try known selectors
    const btn = document.querySelector(".btn-next, .next, [data-action='next']") || findButtonByText("next");
    if (btn) { btn.click(); return; }
    // fallback: dispatch custom event
    document.dispatchEvent(new CustomEvent("swipe:next"));
  }

  function triggerPrev() {
    if (typeof window.prevNews === "function") {
      window.prevNews();
      return;
    }
    const btn = document.querySelector(".btn-prev, .prev, [data-action='prev']") || findButtonByText("prev");
    if (btn) { btn.click(); return; }
    document.dispatchEvent(new CustomEvent("swipe:prev"));
  }

  // touchstart / pointerdown
  function onStart(x, y) {
    startX = x;
    startY = y;
    startTime = Date.now();
    tracking = true;
  }

  // touchend / pointerup
  function onEnd(x, y) {
    if (!tracking) return;
    const distX = x - startX;
    const distY = y - startY;
    const elapsed = Date.now() - startTime;
    tracking = false;

    // ignore long gestures
    if (elapsed > MAX_TIME) return;

    if (Math.abs(distY) >= THRESHOLD && Math.abs(distX) < MAX_HORIZONTAL) {
      // swipe up => distY negative (moved up)
      if (distY < 0) {
        triggerNext();
      } else {
        triggerPrev();
      }
    }
  }

  // Touch handlers
  document.addEventListener("touchstart", function (e) {
    if (!e.touches || e.touches.length > 1) return; // ignore multi-touch
    const t = e.touches[0];
    // if started on input/textarea, ignore (user wants to type/scroll)
    if (isFormElement(e.target)) return;
    onStart(t.clientX, t.clientY);
  }, { passive: true });

  document.addEventListener("touchend", function (e) {
    // touchend has no touches, but changedTouches
    const t = (e.changedTouches && e.changedTouches[0]) || null;
    if (!t) { tracking = false; return; }
    onEnd(t.clientX, t.clientY);
  }, { passive: true });

  // pointer events fallback for desktop / some devices
  document.addEventListener("pointerdown", function (e) {
    // only track primary pointer (left mouse / finger)
    if (!e.isPrimary) return;
    if (isFormElement(e.target)) return;
    onStart(e.clientX, e.clientY);
  });

  document.addEventListener("pointerup", function (e) {
    if (!e.isPrimary) return;
    onEnd(e.clientX, e.clientY);
  });

  // optional: keyboard arrows (up/down) support
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      triggerNext();
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      triggerPrev();
    }
  });

  // debug: expose small helpers
  window.__swipe_debug = {
    triggerNext: triggerNext,
    triggerPrev: triggerPrev
  };

  // avoid interfering with normal page vertical scroll when user scrolls within text:
  // We only act on relatively quick gestures (max time) and with limited horizontal movement.
  // That keeps standard scrolling working fine.
})();
