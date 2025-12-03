// static/js/render.js
import { setCurrentNews, getCurrentNews } from "./state.js";

const titleEl = document.getElementById("news-title");
const summaryEl = document.getElementById("news-summary");
const loadingEl = document.getElementById("news-loading");
const cardEl = document.getElementById("news-card");
const moreInfoBtn = document.getElementById("more-info-btn");

const likeBtn = document.getElementById("like-btn");
const dislikeBtn = document.getElementById("dislike-btn");
const likeCountEl = document.getElementById("like-count");
const dislikeCountEl = document.getElementById("dislike-count");

export function setLoading(isLoading) {
  if (!loadingEl) return;

  if (isLoading) {
    loadingEl.style.display = "block";
  } else {
    loadingEl.style.display = "none";
  }
}

export function renderNews(item) {
  setCurrentNews(item);

  if (!item) {
    if (titleEl) titleEl.textContent = "న్యూస్ అందుబాటులో లేదు";
    if (summaryEl) summaryEl.textContent = "తర్వాత మళ్లీ ప్రయత్నించండి.";
    if (moreInfoBtn) {
      moreInfoBtn.href = "#";
      moreInfoBtn.target = "_self";
    }
    if (cardEl) {
      cardEl.dataset.newsId = "";
    }
    if (likeCountEl) likeCountEl.textContent = "0";
    if (dislikeCountEl) dislikeCountEl.textContent = "0";
    return;
  }

  if (titleEl) titleEl.textContent = item.title;
  if (summaryEl) summaryEl.textContent = item.summary;

  if (cardEl) {
    cardEl.dataset.newsId = item.id || "";
  }

  if (moreInfoBtn) {
    moreInfoBtn.href = item.link || "#";
    moreInfoBtn.target = "_blank";
  }

  if (likeCountEl) likeCountEl.textContent = String(item.likes ?? 0);
  if (dislikeCountEl) dislikeCountEl.textContent = String(item.dislikes ?? 0);

  setLoading(false);
}

export function getCurrentNewsId() {
  const fromState = getCurrentNews();
  if (fromState && fromState.id) return fromState.id;

  if (cardEl && cardEl.dataset.newsId) return cardEl.dataset.newsId;

  return null;
}

export function updateReactionCounts(deltaLikes, deltaDislikes) {
  if (likeCountEl && typeof deltaLikes === "number") {
    likeCountEl.textContent = String(deltaLikes);
  }
  if (dislikeCountEl && typeof deltaDislikes === "number") {
    dislikeCountEl.textContent = String(deltaDislikes);
  }
}
