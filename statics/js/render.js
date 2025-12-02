// render.js
import {
  state,
  getItems,
  getCurrentIndex,
  getItemId,
  getReactions,
  getComments
} from "./state.js";

const root = document.getElementById("news-root");

function extractUrl(item) {
  return (
    item.original_link ||
    item.link ||
    item.url ||
    (item.source && item.source.url) ||
    "#"
  );
}

function extractTitle(item) {
  return item.title || item.heading || "శీర్షిక అందుబాటులో లేదు";
}

function extractSummary(item) {
  return (
    item.summary ||
    item.description ||
    item.content ||
    "ఈ న్యూస్ కు సమ్మరీ అందుబాటులో లేదు."
  );
}

export function showLoading() {
  root.innerHTML = `
    <article class="card card--loading">
      <div class="card-body">
        <p>న్యూస్ లోడ్ అవుతోంది...</p>
      </div>
    </article>
  `;
}

export function showError(msg) {
  root.innerHTML = `
    <article class="card card--error">
      <div class="card-body">
        <p>${msg || "న్యూస్ లోడ్ కాలేదు. కాసేపు తర్వాత ప్రయత్నించండి."}</p>
      </div>
    </article>
  `;
}

export function renderCurrent(direction = "up") {
  const items = getItems();
  const idx = getCurrentIndex();

  if (!items.length) {
    showError("ప్రస్తుతం న్యూస్ అందుబాటులో లేదు.");
    return;
  }

  const item = items[idx];
  const id = getItemId(item, idx);
  const url = extractUrl(item);
  const title = extractTitle(item);
  const summary = extractSummary(item);
  const reactions = getReactions(id);
  const comments = getComments(id);

  const animClass =
    direction === "down" ? "card-enter-down" : "card-enter-up";

  root.innerHTML = `
    <article class="card ${animClass}" data-id="${id}">
      <header>
        <h2 class="card-title">${title}</h2>
      </header>

      <section class="card-body">
        <p>${summary}</p>
      </section>

      <footer class="card-footer">
        <div class="feedback-row">
          <div class="reactions">
            <button class="reaction-btn reaction-btn--like" data-action="like">
              ❤️ <span class="count">${reactions.like}</span>
            </button>
            <button class="reaction-btn reaction-btn--dislike" data-action="dislike">
              👎 <span class="count">${reactions.dislike}</span>
            </button>
          </div>
          <button class="comments-toggle" data-action="toggle-comments">
            కామెంట్స్ (${comments.length})
          </button>
        </div>

        <section class="comments-section" data-comments>
          <textarea
            class="comment-input"
            placeholder="మీ అభిప్రాయం ఇక్కడ రాయండి..."
          ></textarea>
          <button class="comment-submit" data-action="submit-comment">
            కామెంట్ పంపండి
          </button>
          <div class="comments-list">
            ${comments
              .map((c) => `<div class="comment-item">${c}</div>`)
              .join("")}
          </div>
        </section>

        <a
          class="read-more-btn"
          href="${url}"
          target="_blank"
          rel="noopener noreferrer"
        >
          పూర్తి వార్త చదవండి
        </a>
      </footer>
    </article>
  `;

  // నా లైక్/డిస్‌లైక్ స్టేటస్ ప్రకారం బటన్ల రంగులు
  const card = root.querySelector(".card");
  const likeBtn = card.querySelector('[data-action="like"]');
  const dislikeBtn = card.querySelector('[data-action="dislike"]');

  if (reactions.my === "like") {
    likeBtn.classList.add("active");
    dislikeBtn.classList.remove("active");
  } else if (reactions.my === "dislike") {
    dislikeBtn.classList.add("active");
    likeBtn.classList.remove("active");
  } else {
    likeBtn.classList.remove("active");
    dislikeBtn.classList.remove("active");
  }
}
