// static/js/state.js
// Simple global state for currently visible news item

window.NewsState = {
  currentItem: null,
};

window.setCurrentNews = function setCurrentNews(item) {
  window.NewsState.currentItem = item || null;
};

window.getCurrentNews = function getCurrentNews() {
  return window.NewsState.currentItem;
};
