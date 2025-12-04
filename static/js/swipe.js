// Replace your existing static/js/swipe.js with this exact file.
// Behaves:
// - Swipe UP  (finger moves up)  => triggers "Next" button
// - Swipe DOWN(finger moves down)=> triggers "Prev" button
// Also supports mouse wheel (optional) for desktops.

(function () {
  const THRESHOLD = 50; // px minimum to count as swipe

  let startY = null;
  let startTime = null;

  function findAndClickButton(nameLower) {
    // try to find a visible button whose text includes nameLower
    const buttons = Array.from(document.querySelectorAll("button, a"));
    for (const b of buttons) {
      try {
        const txt = (b.innerText || b.textContent || "").trim().toLowerCase();
        if (!txt) continue;
        if (txt.includes(nameLower)) {
          b.click();
          return true;
        }
      } catch (e) {
        // ignore
      }
    }
    return false;
  }

  function onTouchStart(e) {
    if (!e.touches || e.touches.length === 0) return;
    startY = e.touches[0].clientY;
    startTime = Date.now();
  }

  function onTouchEnd(e) {
    if (startY === null) return;
    // if changedTouches present
    const touch = (e.changedTouches && e.changedTouches[0]) || null;
    const endY = touch ? touch.clientY : null;
    if (endY === null) {
      startY = null;
      return;
    }
    const dy = endY - startY;
    const dt = Date.now() - (startTime || Date.now());

    // quick swipe guard: require some movement
    if (Math.abs(dy) < THRESHOLD) {
      startY = null;
      return;
    }

    if (dy < 0) {
      // finger moved up (swipe up) => Next
      const clicked = findAndClickButton("next") || findAndClickButton("నెక్స్ట్") || findAndClickButton("మరింత");
      // fallback: call window.nextArticle() if exists
      if (!clicked && typeof window.nextArticle === "function") window.nextArticle();
    } else {
      // finger moved down (swipe down) => Prev
      const clicked = findAndClickButton("prev") || findAndClickButton("prev") || findAndClickButton("పీవ్యూ") || findAndClickButton("prev");
      if (!clicked && typeof window.prevArticle === "function") window.prevArticle();
    }

    startY = null;
  }

  // wheel support: scroll up/down -> next/prev (optional)
  function onWheel(e) {
    // ignore if ctrl/shift pressed
    if (e.ctrlKey || e.shiftKey || e.metaKey) return;
    if (Math.abs(e.deltaY) < 10) return;
    if (e.deltaY > 0) {
      // scroll down -> show Prev (per your request: down swipe => prev)
      findAndClickButton("prev") || (typeof window.prevArticle === "function" && window.prevArticle());
    } else {
      // scroll up -> show Next
      findAndClickButton("next") || (typeof window.nextArticle === "function" && window.nextArticle());
    }
  }

  // attach listeners to the main content area if exists, otherwise document
  const mount = document.querySelector("main") || document.querySelector("#app") || document;

  mount.addEventListener("touchstart", onTouchStart, { passive: true });
  mount.addEventListener("touchend", onTouchEnd, { passive: true });
  // wheel on desktop
  mount.addEventListener("wheel", onWheel, { passive: true });

  // small helpful log to confirm file loaded (remove later if you want)
  console.info("swipe.js loaded — swipe up => NEXT, swipe down => PREV");

})();
