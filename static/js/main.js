// static/js/main.js
// Boots the whole UI – this is the brain

async function loadNews(direction) {
  try {
    const item = await window.fetchNewsItem(direction);
    window.setCurrentNews(item);
    window.renderNewsCard(item);
  } catch (err) {
    console.error(err);
    window.showNewsError("సమాచారం లోడ్ కాలేదు. కొంచెం తర్వాత మళ్లీ ప్రయత్నించండి.");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  const card = document.getElementById("news-card");

  // swipe (up -> next, down -> prev)
  window.attachSwipeHandlers(card, {
    onNext: () => loadNews("next"),
    onPrev: () => loadNews("prev"),
  });

  // like / dislike
  window.setupLikeButtons();

  // comments
  window.setupComments();

  // initial news
  loadNews();
});
