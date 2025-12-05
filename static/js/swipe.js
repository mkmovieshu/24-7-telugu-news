// static/js/swipe.js
// Replace your existing swipe.js with this file
// Assumes you include it as module or normal script after render.js and state.js.
// If using modules: <script type="module" src="/static/js/swipe.js"></script>

import { nextNews, prevNews } from './render.js'; // these functions call state.moveNext/movePrev and render

// If import fails in non-module environment, try fallback to window functions.
function getFns() {
  if (typeof nextNews === 'function' && typeof prevNews === 'function') {
    return { nextNews, prevNews };
  }
  // fallback — if render.js attached functions globally:
  return {
    nextNews: window.nextNews || function(){ console.warn('nextNews not found'); },
    prevNews: window.prevNews || function(){ console.warn('prevNews not found'); }
  };
}

const { nextNews: doNext, prevNews: doPrev } = getFns();

let startY = 0;
let startX = 0;
let tracking = false;

const threshold = 50; // min px for swipe
const restraint = 100; // max x-axis movement allowed

function touchStart(e) {
  const t = e.touches ? e.touches[0] : e;
  startY = t.clientY;
  startX = t.clientX;
  tracking = true;
}

function touchEnd(e) {
  if (!tracking) return;
  const t = (e.changedTouches && e.changedTouches[0]) || e;
  const distY = startY - t.clientY; // positive => swipe up
  const distX = startX - t.clientX;
  tracking = false;

  if (Math.abs(distX) > restraint) {
    // horizontal move — ignore
    return;
  }
  if (Math.abs(distY) < threshold) {
    // too small
    return;
  }

  if (distY > 0) {
    // swipe up => next
    try { doNext(); } catch (err) { console.error('doNext failed', err); }
  } else {
    // swipe down => prev
    try { doPrev(); } catch (err) { console.error('doPrev failed', err); }
  }
}

// attach listeners to document / main card container
const attachSwipe = (el = document) => {
  el.addEventListener('touchstart', touchStart, { passive: true });
  el.addEventListener('touchend', touchEnd, { passive: true });
  // desktop mouse fallback
  let mouseDown = false;
  el.addEventListener('mousedown', (ev) => { mouseDown = true; touchStart(ev); });
  el.addEventListener('mouseup', (ev) => { if (mouseDown) { mouseDown = false; touchEnd(ev); } });
};

window.addEventListener('DOMContentLoaded', () => {
  // prefer card container id if available
  const container = document.getElementById('news-card') || document.getElementById('app-container') || document;
  attachSwipe(container);
});
