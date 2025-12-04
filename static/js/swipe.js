// static/js/swipe.js
// Improved vertical swipe: up => next, down => prev
// Adds touchmove handling and prevents native scroll when gesture detected.

(function () {
  const THRESHOLD = 60; // vertical px to count as swipe
  const MAX_HORIZONTAL = 100; // disallow if too much horizontal movement
  const MAX_TIME = 1000; // ms

  let startX = 0, startY = 0, startTime = 0;
  let tracking = false;
  let moved = false; // whether touchmove exceeded small slop

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
      if (t.indexOf(lower) === 0) return b;
    }
    return null;
  }

  function triggerNext() {
    if (typeof window.nextNews === "function") { window.nextNews(); return; }
    const btn = document.querySelector(".btn-next, .next, [data-action='next']") || findButtonByText("next");
    if (btn) { btn.click(); return; }
    document.dispatchEvent(new CustomEvent("swipe:next"));
  }

  function triggerPrev() {
    if (typeof window.prevNews === "function") { window.prevNews(); return; }
    const btn = document.querySelector(".btn-prev, .prev, [data-action='prev']") || findButtonByText("prev");
    if (btn) { btn.click(); return; }
    document.dispatchEvent(new CustomEvent("swipe:prev"));
  }

  function onStart(x, y) {
    startX = x; startY = y; startTime = Date.now();
    tracking = true; moved = false;
  }

  function onEnd(x, y) {
    if (!tracking) return;
    const distX = x - startX;
    const distY = y - startY;
    const elapsed = Date.now() - startTime;
    tracking = false; moved = false;

    if (elapsed > MAX_TIME) return;

    if (Math.abs(distY) >= THRESHOLD && Math.abs(distX) < MAX_HORIZONTAL) {
      if (distY < 0) triggerNext(); else triggerPrev();
    }
  }

  // TOUCH EVENTS (note: passive:false on touchstart to allow preventDefault in touchmove)
  document.addEventListener("touchstart", function (e) {
    if (!e.touches || e.touches.length > 1) return;
    const t = e.touches[0];
    if (isFormElement(e.target)) return;
    onStart(t.clientX, t.clientY);
  }, { passive: false });

  document.addEventListener("touchmove", function (e) {
    if (!tracking) return;
    const t = e.touches && e.touches[0];
    if (!t) return;
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;

    // if vertical movement dominates and already beyond small slop, prevent page scroll
    if (Math.abs(dy) > 10 && Math.abs(dy) > Math.abs(dx)) {
      moved = true;
      // if vertical movement large and primarily vertical, stop native scroll so we can handle swipe
      if (Math.abs(dy) > 20 && Math.abs(dx) < MAX_HORIZONTAL) {
        // prevent default to avoid page pull-to-refresh or native scroll interfering
        e.preventDefault();
      }
    }
  }, { passive: false });

  document.addEventListener("touchend", function (e) {
    if (!tracking) return;
    const t = (e.changedTouches && e.changedTouches[0]) || null;
    if (!t) { tracking = false; return; }
    onEnd(t.clientX, t.clientY);
  }, { passive: true });

  document.addEventListener("touchcancel", function () {
    tracking = false; moved = false;
  });

  // POINTER EVENTS fallback
  document.addEventListener("pointerdown", function (e) {
    if (!e.isPrimary) return;
    if (isFormElement(e.target)) return;
    onStart(e.clientX, e.clientY);
  });

  document.addEventListener("pointermove", function (e) {
    if (!tracking || !e.isPrimary) return;
    const dx = e.clientX - startX, dy = e.clientY - startY;
    if (Math.abs(dy) > 10 && Math.abs(dy) > Math.abs(dx)) {
      moved = true;
      // optionally preventDefault for pointer events if supported (not always necessary)
      if (typeof e.preventDefault === "function" && Math.abs(dy) > 20 && Math.abs(dx) < MAX_HORIZONTAL) {
        try { e.preventDefault(); } catch (err) { /* ignore */ }
      }
    }
  });

  document.addEventListener("pointerup", function (e) {
    if (!e.isPrimary) return;
    onEnd(e.clientX, e.clientY);
  });

  document.addEventListener("pointercancel", function () {
    tracking = false; moved = false;
  });

  // keyboard convenience
  document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowUp") { e.preventDefault(); triggerNext(); }
    else if (e.key === "ArrowDown") { e.preventDefault(); triggerPrev(); }
  });

  // helpers exposed for debugging
  window.__swipe_debug = {
    triggerNext, triggerPrev
  };

})();
