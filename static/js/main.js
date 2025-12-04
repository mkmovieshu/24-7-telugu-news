// main.js (entry)
import { fetchNewsList, sendReaction } from "./api.js";
import { loadCommentsForNews, saveCommentForNews } from "./comments.js";

console.log("[main] boot");

const els = {
  newsTitle: document.getElementById("news-title"),
  newsSummary: document.getElementById("news-summary"),
  likeBtn: document.getElementById("like-btn"),
  dislikeBtn: document.getElementById("dislike-btn"),
  likeCount: document.getElementById("like-count"),
  dislikeCount: document.getElementById("dislike-count"),
  moreInfoBtn: document.getElementById("more-info-btn"),
  commentInput: document.getElementById("comment-text"),
  saveCommentBtn: document.getElementById("save-comment-btn"),
  commentsList: document.getElementById("comments-list"),
};

let newsList = [];
let idx = 0;

function renderCurrent() {
  const item = newsList[idx];
  if (!item) {
    els.newsTitle.textContent = "టైటిల్ లేదు";
    els.newsSummary.textContent = "న్యూస్ లేదు";
    els.likeCount.textContent = "0";
    els.dislikeCount.textContent = "0";
    els.commentsList.innerHTML = "";
    return;
  }
  els.newsTitle.textContent = item.title || "";
  els.newsSummary.textContent = item.summary || "";
  els.likeCount.textContent = String(item.likes || 0);
  els.dislikeCount.textContent = String(item.dislikes || 0);

  // load comments for this news
  loadCommentsForNews(item.id, els.commentsList).catch(e => {
    console.error("[main] loadComments error", e);
  });
}

async function loadAllNews() {
  try {
    console.log("[main] loading news...");
    newsList = await fetchNewsList();
    idx = 0;
    renderCurrent();
    console.log("[main] news loaded", newsList.length);
  } catch (err) {
    console.error("[main] failed to load news", err);
    els.newsTitle.textContent = "నెట్వర్క్ లోపం";
    els.newsSummary.textContent = "న్యూస్ లిస్ట్ తీసుకురాలేదు";
  }
}

els.likeBtn.addEventListener("click", async () => {
  const cur = newsList[idx];
  if (!cur) return;
  try {
    const resp = await sendReaction(cur.id, "like");
    els.likeCount.textContent = String(resp.likes || 0);
    console.log("[main] liked", resp);
  } catch (err) {
    console.error("[main] like failed", err);
    alert("Like failed");
  }
});

els.dislikeBtn.addEventListener("click", async () => {
  const cur = newsList[idx];
  if (!cur) return;
  try {
    const resp = await sendReaction(cur.id, "dislike");
    els.dislikeCount.textContent = String(resp.dislikes || 0);
  } catch (err) {
    console.error("[main] dislike failed", err);
    alert("Dislike failed");
  }
});

els.moreInfoBtn.addEventListener("click", () => {
  const cur = newsList[idx];
  if (!cur) return;
  if (cur.link) window.open(cur.link, "_blank");
});

els.saveCommentBtn.addEventListener("click", async () => {
  const cur = newsList[idx];
  const text = (els.commentInput.value || "").trim();
  if (!cur || !text) {
    alert("Enter comment");
    return;
  }
  try {
    await saveCommentForNews(cur.id, text);
    // refresh comments
    els.commentInput.value = "";
    await loadCommentsForNews(cur.id, els.commentsList);
  } catch (err) {
    console.error("[main] comment save failed", err);
    alert("Failed to save comment");
  }
});

// Simple swipe: next news when body clicked (or you can add gesture lib)
document.body.addEventListener("click", (e) => {
  // ignore clicks on buttons/inputs
  if (e.target.closest("button") || e.target.closest("input")) return;
  // next
  if (!newsList || newsList.length === 0) return;
  idx = (idx + 1) % newsList.length;
  renderCurrent();
});

window.addEventListener("load", () => {
  loadAllNews();
});
