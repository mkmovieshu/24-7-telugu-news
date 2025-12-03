// static/js/render.js
// Renders a news item into the card

window.renderNewsCard = function renderNewsCard(item) {
  const card = document.getElementById("news-card");
  if (!card) return;

  const titleEl =
    card.querySelector(".news-title") ||
    document.getElementById("news-title");
  const summaryEl =
    card.querySelector(".news-summary") ||
    document.getElementById("news-summary");
  const moreBtn = document.getElementById("more-info-btn");
  const likeCountEl = document.getElementById("like-count");
  const dislikeCountEl = document.getElementById("dislike-count");

  if (!item) {
    if (titleEl) titleEl.textContent = "Loading...";
    if (summaryEl) summaryEl.textContent = "న్యూస్ లోడ్ అవుతోంది...";
    card.dataset.newsId = "";
    if (moreBtn) moreBtn.style.display = "none";
    if (likeCountEl) likeCountEl.textContent = "0";
    if (dislikeCountEl) dislikeCountEl.textContent = "0";
    return;
  }

  // save current id on card so likes/comments use it
  if (item.id) {
    card.dataset.newsId = item.id;
  } else if (item._id) {
    // just in case API returns _id
    card.dataset.newsId = item._id;
  } else {
    card.dataset.newsId = "";
  }

  const title = item.title || "టైటిల్ లేదు";
  const summary =
    item.summary || item.raw_summary || "ఈ వార్తకు సమరీ అందుబాటులో లేదు.";

  if (titleEl) titleEl.textContent = title;
  if (summaryEl) summaryEl.textContent = summary;

  if (moreBtn) {
    if (item.link) {
      moreBtn.style.display = "block";
      moreBtn.onclick = () => {
        window.open(item.link, "_blank", "noopener");
      };
    } else {
      moreBtn.style.display = "none";
      moreBtn.onclick = null;
    }
  }

  if (likeCountEl) likeCountEl.textContent = String(item.likes ?? 0);
  if (dislikeCountEl) dislikeCountEl.textContent = String(item.dislikes ?? 0);
};

window.showNewsError = function showNewsError(message) {
  const card = document.getElementById("news-card");
  if (!card) return;
  const titleEl =
    card.querySelector(".news-title") ||
    document.getElementById("news-title");
  const summaryEl =
    card.querySelector(".news-summary") ||
    document.getElementById("news-summary");

  if (titleEl) titleEl.textContent = "లోపం వచ్చింది";
  if (summaryEl) summaryEl.textContent = message || "కొంచెం తర్వాత మళ్లీ ప్రయత్నించండి.";
};
