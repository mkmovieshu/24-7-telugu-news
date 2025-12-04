// /opt/render/project/src/static/js/main.js
// REPLACE the entire file with this content (single-step fix)
// Purpose: add robust image fallback (inline SVG) and error capture so news keeps loading.

import { fetchNews } from "./api.js";
import { loadCommentsForCurrent } from "./comments.js";
import { updateLikesUI } from "./likes.js";

let state = {
  items: [],
  idx: 0
};

const $ = sel => document.querySelector(sel);

// inline SVG placeholder (data URL) so we don't depend on placeholder.png file
const INLINE_PLACEHOLDER = 'data:image/svg+xml;utf8,' + encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="600" viewBox="0 0 1200 600">
  <rect width="100%" height="100%" fill="#ececec"/>
  <g fill="#d6d6d6" font-family="Arial, sans-serif" font-size="28">
    <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle">No image</text>
  </g>
</svg>`);

function safeSetImage($img, url) {
  if (!$img) return;
  if (!url) {
    $img.src = INLINE_PLACEHOLDER;
    return;
  }
  // set image and attach error fallback
  $img.onerror = () => {
    // prevent infinite loop
    $img.onerror = null;
    $img.src = INLINE_PLACEHOLDER;
  };
  $img.src = url;
}

function applyTransitionAndRender(direction) {
  const card = document.getElementById("news-card");
  if (!card) { renderCurrent(); return; }

  if (direction === "up") {
    card.classList.add("slide-up");
  } else if (direction === "down") {
    card.classList.add("slide-down");
  }

  setTimeout(() => {
    card.classList.remove("slide-up");
    card.classList.remove("slide-down");
    renderCurrent();
  }, 260);
}

function renderCurrent() {
  const item = state.items[state.idx];
  const $img = document.getElementById("news-image");
  try {
    if (!item) {
      $("#news-title").textContent = "న్యూస్ టైటిల్ రాలేదు";
      $("#news-summary").textContent = "న్యూస్ లోడ్ అవుతోంది...";
      $("#news-link").href = "#";
      $("#likes-count").textContent = 0;
      $("#dislikes-count").textContent = 0;
      $("#comments-list").innerHTML = "";
      safeSetImage($img, null);
      return;
    }

    $("#news-title").textContent = item.title || "";
    $("#news-summary").textContent = item.summary || "";
    $("#news-link").href = item.link || "#";
    $("#likes-count").textContent = item.likes || 0;
    $("#dislikes-count").textContent = item.dislikes || 0;

    // use item.image or item.thumbnail or fallback to INLINE_PLACEHOLDER
    const imgUrl = item.image || item.thumbnail || null;
    safeSetImage($img, imgUrl);

    // Load comments and likes UI (these functions should gracefully handle errors)
    loadCommentsForCurrent(item.id).catch(err => {
      console.warn("loadCommentsForCurrent error", err);
      // degrade silently by clearing comments list
      const cl = document.getElementById("comments-list");
      if (cl) cl.innerHTML = "";
    });
    updateLikesUI(item.id, item.likes, item.dislikes);
  } catch (err) {
    console.error("renderCurrent error", err);
    showTopError("Render failed: " + (err.message || String(err)));
  }
}

export function moveNext() {
  if (!state.items || state.items.length === 0) return;
  if (state.idx < state.items.length - 1) {
    state.idx = state.idx + 1;
    applyTransitionAndRender("up");
  }
}

export function movePrev() {
  if (!state.items || state.items.length === 0) return;
  if (state.idx > 0) {
    state.idx = state.idx - 1;
    applyTransitionAndRender("down");
  }
}

function showTopError(msg) {
  // create or update a small floating error box so you can see issues on mobile
  let el = document.getElementById("js-error-box");
  if (!el) {
    el = document.createElement("div");
    el.id = "js-error-box";
    el.style.position = "fixed";
    el.style.left = "12px";
    el.style.right = "12px";
    el.style.bottom = "14px";
    el.style.zIndex = 9999;
    el.style.background = "rgba(0,0,0,0.8)";
    el.style.color = "#fff";
    el.style.padding = "10px 12px";
    el.style.borderRadius = "8px";
    el.style.fontSize = "13px";
    el.style.boxShadow = "0 8px 24px rgba(0,0,0,0.2)";
    document.body.appendChild(el);
  }
  el.textContent = msg;
  // auto-hide after 7s
  clearTimeout(el._hideT);
  el._hideT = setTimeout(()=> {
    if (el && el.parentNode) el.parentNode.removeChild(el);
  }, 7000);
}

async function init() {
  try {
    const json = await fetchNews(100);
    state.items = json.items || [];
    state.idx = 0;
    renderCurrent();
  } catch (err) {
    console.error("init error", err);
    showTopError("Init error: " + (err.message || String(err)));
    // also render a friendly message in the card
    $("#news-title").textContent = "న్యూస్ లోడ్ తప్పింది";
    $("#news-summary").textContent = `Error loading news. Tap Debug or check logs.`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const nextBtn = document.getElementById("next-btn");
  if (nextBtn) nextBtn.addEventListener("click", () => moveNext());
  const prevBtn = document.getElementById("prev-btn");
  if (prevBtn) prevBtn.addEventListener("click", () => movePrev());

  // keyboard shortcuts for testing (optional)
  document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") moveNext();
    if (e.key === "ArrowDown") movePrev();
  });

  // start
  init();
});
