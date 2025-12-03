import { getCurrentNews } from "./state.js";

const cardEl = document.getElementById("news-card");
const titleEl = document.getElementById("news-title");
const summaryEl = document.getElementById("news-summary");
const moreBtn = document.getElementById("more-info-btn");

const likeCountEl = document.getElementById("like-count");
const dislikeCountEl = document.getElementById("dislike-count");

function setFallback() {
  titleEl.textContent = "టైటిల్ లేదు";
  summaryEl.textContent = "ఈ వార్తకు సమరీ అందుబాటులో లేదు.";
  moreBtn.onclick = null;
  likeCountEl.textContent = "0";
  dislikeCountEl.textContent = "0";
  cardEl.dataset.id = "";
}

/**
 * direction: "initial" | "next" | "prev"
 */
export function renderNewsCard(item, direction = "initial") {
  if (!item) {
    setFallback();
    return;
  }

  // animation classes
  cardEl.classList.remove("slide-up", "slide-down");
  // force reflow
  void cardEl.offsetWidth;

  if (direction === "next") {
    cardEl.classList.add("slide-up");
  } else if (direction === "prev") {
    cardEl.classList.add("slide-down");
  }

  titleEl.textContent = item.title || "టైటిల్ లేదు";
  summaryEl.textContent =
    item.summary || "ఈ వార్తకు సమరీ అందుబాటులో లేదు.";

  likeCountEl.textContent = item.likes ?? 0;
  dislikeCountEl.textContent = item.dislikes ?? 0;

  cardEl.dataset.id = item.id || "";

  moreBtn.onclick = () => {
    if (item.link) {
      window.open(item.link, "_blank");
    }
  };
}

// external helper – లైక్స్ అప్డేట్ కోసం
export function updateReactions(likes, dislikes) {
  likeCountEl.textContent = likes ?? likeCountEl.textContent;
  dislikeCountEl.textContent = dislikes ?? dislikeCountEl.textContent;
}

// initial loading fallback
export function renderInitialLoading() {
  const current = getCurrentNews();
  if (!current) {
    setFallback();
  } else {
    renderNewsCard(current, "initial");
  }
}
