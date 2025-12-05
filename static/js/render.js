// static/js/render.js
import { getCurrentNews } from "./state.js";

const cardEl = document.getElementById("news-card");
const titleEl = document.getElementById("news-title");
const summaryEl = document.getElementById("news-summary");
const moreBtn = document.getElementById("more-info-btn");
const likeCountEl = document.getElementById("like-count");
const dislikeCountEl = document.getElementById("dislike-count");
const imageEl = document.getElementById("news-image");

function setFallback() {
  titleEl.textContent = "టైటిల్ లేదు";
  summaryEl.textContent = "న్యూస్ లోడ్ అవుతోంది...";
  likeCountEl.textContent = "0";
  dislikeCountEl.textContent = "0";
  imageEl.style.display = "none";
  cardEl.dataset.id = "";
  moreBtn.onclick = null;
}

export function renderNewsCard(item, direction = "initial") {
  if (!item) {
    setFallback();
    return;
  }

  // reset animation
  cardEl.classList.remove("slide-up", "slide-down");
  void cardEl.offsetWidth;

  if (direction === "next") cardEl.classList.add("slide-up");
  if (direction === "prev") cardEl.classList.add("slide-down");

  titleEl.textContent = item.title || "టైటిల్ లేదు";
  summaryEl.textContent = item.summary || "";
  likeCountEl.textContent = (item.likes !== undefined) ? item.likes : 0;
  dislikeCountEl.textContent = (item.dislikes !== undefined) ? item.dislikes : 0;
  cardEl.dataset.id = item.id || "";

  if (item.image) {
    imageEl.src = item.image;
    imageEl.style.display = "block";
    imageEl.onclick = () => {
      if (item.link) window.open(item.link, "_blank");
    };
  } else {
    imageEl.style.display = "none";
  }

  moreBtn.onclick = () => {
    if (item.link) window.open(item.link, "_blank");
  };
}

export function updateReactions(likes, dislikes) {
  if (likes !== undefined) likeCountEl.textContent = likes;
  if (dislikes !== undefined) dislikeCountEl.textContent = dislikes;
}

export function renderInitial() {
  const current = getCurrentNews();
  if (!current) {
    setFallback();
  } else {
    renderNewsCard(current, "initial");
  }
}
