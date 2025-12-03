// static/js/likes.js
// Like / Dislike buttons

window.setupLikeButtons = function setupLikeButtons() {
  const likeBtn = document.getElementById("like-btn");
  const dislikeBtn = document.getElementById("dislike-btn");
  const likeCountEl = document.getElementById("like-count");
  const dislikeCountEl = document.getElementById("dislike-count");

  if (!likeBtn || !dislikeBtn) return;

  likeBtn.onclick = async () => {
    const item = window.getCurrentNews();
    if (!item) return;

    const newsId = item.id || item._id;
    if (!newsId) return;

    try {
      await window.sendReaction(newsId, "like");
      const current = Number(likeCountEl?.textContent || "0") + 1;
      if (likeCountEl) likeCountEl.textContent = String(current);
      likeBtn.classList.add("active-like");
      dislikeBtn.classList.remove("active-dislike");
    } catch (e) {
      console.error(e);
      alert("లైక్ నమోదు కాలేదు. కొంచెం తర్వాత మళ్లీ ప్రయత్నించండి.");
    }
  };

  dislikeBtn.onclick = async () => {
    const item = window.getCurrentNews();
    if (!item) return;
    const newsId = item.id || item._id;
    if (!newsId) return;

    try {
      await window.sendReaction(newsId, "dislike");
      const current = Number(dislikeCountEl?.textContent || "0") + 1;
      if (dislikeCountEl) dislikeCountEl.textContent = String(current);
      dislikeBtn.classList.add("active-dislike");
      likeBtn.classList.remove("active-like");
    } catch (e) {
      console.error(e);
      alert("డిస్‌లైక్ నమోదు కాలేదు. కొంచెం తర్వాత మళ్లీ ప్రయత్నించండి.");
    }
  };
};
