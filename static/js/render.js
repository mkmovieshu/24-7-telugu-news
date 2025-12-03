// static/js/render.js

import { getLoading } from "./state.js";

const cardEl = document.getElementById("news-card");
const titleEl = document.getElementById("news-title");
const summaryEl = document.getElementById("news-summary");
const moreInfoBtn = document.getElementById("more-info-btn");
const likeCountEl = document.getElementById("like-count");
const dislikeCountEl = document.getElementById("dislike-count");

// loading / error / news render

export function renderLoading() {
  if (!cardEl || !titleEl || !summaryEl) return;
  cardEl.classList.add("loading");
  titleEl.textContent = "Loading...";
  summaryEl.textContent = "న్యూస్ లోడ్ అవుతోంది...";
}

export function renderError(message) {
  if (!cardEl || !titleEl || !summaryEl) return;
  cardEl.classList.remove("loading");
  titleEl.textContent = "ఎర్రర్ వచ్చింది";
  summaryEl.textContent = message || "న్యూస్ ని లోడ్ చేయలేకపోయాం.";
}

export function renderNews(news) {
  if (!news || !cardEl || !titleEl || !summaryEl) return;

  cardEl.classList.remove("loading");

  // card కి id attach చేస్తాం – likes.js కి ఇదే life
  cardEl.dataset.newsId = news.id || "";

  titleEl.textContent = news.title || "";
  summaryEl.textContent = news.summary || "";

  if (moreInfoBtn) {
    if (news.link) {
      moreInfoBtn.href = news.link;
      moreInfoBtn.target = "_blank";
      moreInfoBtn.rel = "noopener noreferrer";
      moreInfoBtn.classList.remove("disabled");
    } else {
      moreInfoBtn.href = "#";
      moreInfoBtn.classList.add("disabled");
    }
  }

  renderReactions(news);
}

export function renderReactions(news) {
  if (likeCountEl) {
    likeCountEl.textContent =
      typeof news.likes === "number" ? String(news.likes) : "0";
  }
  if (dislikeCountEl) {
    dislikeCountEl.textContent =
      typeof news.dislikes === "number" ? String(news.dislikes) : "0";
  }
}
