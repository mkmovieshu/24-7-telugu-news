// ~/project/static/js/swipe.js - స్వైపింగ్ కోసం అప్‌డేటెడ్ కోడ్

(function () {
  const THRESHOLD = 50; // px minimum to count as swipe

  let startY = null;
  let startTime = null;

  function onTouchStart(e) {
    if (!e.touches || e.touches.length === 0) return;
    startY = e.touches[0].clientY;
    startTime = Date.now();
  }

  function onTouchEnd(e) {
    if (startY === null) return;
    const touch = (e.changedTouches && e.changedTouches[0]) || null;
    const endY = touch ? touch.clientY : null;
    if (endY === null) {
      startY = null;
      return;
    }
    const dy = endY - startY;

    // quick swipe guard: require some movement
    if (Math.abs(dy) < THRESHOLD) {
      startY = null;
      return;
    }

    if (dy < 0) {
      // finger moved up (swipe up) => Next
      // ✅ main.js లోని గ్లోబల్ ఫంక్షన్‌ను కాల్ చేయండి
      if (typeof window.showNext === "function") {
        window.showNext();
        e.preventDefault(); // prevent default scroll
      }
    } else {
      // finger moved down (swipe down) => Prev
      // ✅ main.js లోని గ్లోబల్ ఫంక్షన్‌ను కాల్ చేయండి
      if (typeof window.showPrev === "function") {
        window.showPrev();
        e.preventDefault(); // prevent default scroll
      }
    }

    startY = null;
  }

  // wheel support: scroll up/down -> next/prev (optional)
  function onWheel(e) {
    // ignore if ctrl/shift pressed
    if (e.ctrlKey || e.shiftKey || e.metaKey) return;
    if (Math.abs(e.deltaY) < 10) return;
    
    if (e.deltaY > 0) {
      // scroll down -> show Prev
      if (typeof window.showPrev === "function") window.showPrev();
    } else {
      // scroll up -> show Next
      if (typeof window.showNext === "function") window.showNext();
    }
  }

  // attach listeners to the main content area if exists, otherwise document
  const mount = document.querySelector("main") || document.querySelector("#main-content") || document;

  mount.addEventListener("touchstart", onTouchStart, { passive: true });
  mount.addEventListener("touchend", onTouchEnd, { passive: false }); // passive: false to allow e.preventDefault()
  // wheel on desktop
  mount.addEventListener("wheel", onWheel, { passive: true });

  console.info("swipe.js loaded: Calling window.showNext/showPrev");

})();
// ... (inside onTouchEnd function)
    if (dy < 0) {
      // finger moved up (swipe up) => Next
      if (typeof window.showNext === "function") { // గ్లోబల్ ఫంక్షన్‌ను కాల్ చేస్తుంది
        window.showNext();
        e.preventDefault(); 
      }
    } else {
      // finger moved down (swipe down) => Prev
      if (typeof window.showPrev === "function") { // గ్లోబల్ ఫంక్షన్‌ను కాల్ చేస్తుంది
        window.showPrev();
        e.preventDefault(); 
      }
    }
// ...
