// static/js/main.js (updated for smooth transitions)
import { fetchNews } from "./api.js";
import { loadCommentsForCurrent } from "./comments.js";
import { updateLikesUI } from "./likes.js";

let state = {
  items: [],
  idx: 0
};

const $ = sel => document.querySelector(sel);

function applyTransitionAndRender(direction) {
  // direction: "up" for next, "down" for prev
  const card = document.getElementById("news-card");
  if (!card) { renderCurrent(); return; }

  // apply class
  if (direction === "up") {
    card.classList.add("slide-up");
  } else if (direction === "down") {
    card.classList.add("slide-down");
  }

  // wait for transition then remove and render
  setTimeout(() => {
    // remove and render new content
    card.classList.remove("slide-up");
    card.classList.remove("slide-down");
    renderCurrent();
  }, 260); // matches CSS durations
}

function renderCurrent() {
  const item = state.items[state.idx];
  const $img = document.getElementById("news-image");
  if (!item) {
    $("#news-title").textContent = "టైటిల్ లేదు";
    $("#news-summary").textContent = "న్యూస్ లేదు";
    $("#news-link").href = "#";
    $("#likes-count").textContent = 0;
    $("#dislikes-count").textContent = 0;
    $("#comments-list").innerHTML = "";
    if ($img) $img.src = "/static/img/placeholder.png";
    return;
  }

  $("#news-title").textContent = item.title || "";
  $("#news-summary").textContent = item.summary || "";
  $("#news-link").href = item.link || "#";
  $("#likes-count").textContent = item.likes || 0;
  $("#dislikes-count").textContent = item.dislikes || 0;

  // set image if provided (we expect 'image' field maybe)
  if ($img) {
    if (item.image) {
      $img.src = item.image;
    } else {
      $img.src = "/static/img/placeholder.png";
    }
  }

  // load comments and likes UI
  loadCommentsForCurrent(item.id);
  updateLikesUI(item.id, item.likes, item.dislikes);
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

async function init() {
  try {
    const json = await fetchNews(100);
    state.items = json.items || [];
    state.idx = 0;
    renderCurrent();
  } catch (err) {
    console.error("init error", err);
    $("#news-title").textContent = "న్యూస్ లోడ్ తప్పింది";
    $("#news-summary").textContent = `Error: ${err.message}`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("#next-btn").addEventListener("click", () => moveNext());
  $("#prev-btn").addEventListener("click", () => movePrev());

  // read-more open in new tab - ensure correct link created
  $("#news-link").addEventListener("click", (e) => {
    // nothing to intercept — let default open happen
  });

  init();
});
