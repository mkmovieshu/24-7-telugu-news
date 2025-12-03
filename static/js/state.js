// static/js/state.js

// అప్లికేషన్ state simple గా ఇక్కడే హ్యాండిల్ చేస్తాం

let currentNews = null; // { id, title, summary, link, likes, dislikes }
let isLoading = false;

export function setCurrentNews(news) {
  currentNews = news || null;
}

export function getCurrentNews() {
  return currentNews;
}

export function getCurrentNewsId() {
  return currentNews ? currentNews.id : null;
}

export function setLoading(loading) {
  isLoading = loading;
}

export function getLoading() {
  return isLoading;
}
