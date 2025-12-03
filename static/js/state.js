// static/js/state.js

let currentNews = null;

export function setCurrentNews(item) {
  currentNews = item;
}

export function getCurrentNews() {
  return currentNews;
}

export function hasNews() {
  return !!currentNews;
}
