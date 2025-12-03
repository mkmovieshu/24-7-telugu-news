// Swipe detection: calls callback("next") / callback("prev")

window.Swipe = (function () {
  const MIN_DISTANCE = 40; // px

  function setupSwipe(element, callback) {
    if (!element) return;

    let startY = null;
    let isTouch = false;

    element.addEventListener(
      "touchstart",
      (e) => {
        if (e.touches.length !== 1) return;
        isTouch = true;
        startY = e.touches[0].clientY;
      },
      { passive: true }
    );

    element.addEventListener(
      "touchend",
      (e) => {
        if (!isTouch || startY === null) return;
        const endY = e.changedTouches[0].clientY;
        const diff = startY - endY;

        if (Math.abs(diff) > MIN_DISTANCE) {
          if (diff > 0) {
            callback("next");
          } else {
            callback("prev");
          }
        }

        startY = null;
        isTouch = false;
      },
      { passive: true }
    );

    // Optional: mouse wheel for desktop
    element.addEventListener(
      "wheel",
      (e) => {
        if (Math.abs(e.deltaY) < 20) return;
        if (e.deltaY > 0) {
          callback("next");
        } else {
          callback("prev");
        }
      },
      { passive: true }
    );
  }

  return {
    setupSwipe,
  };
})();
