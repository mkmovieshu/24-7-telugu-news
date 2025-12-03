// News list & current index – ఇదే single source of truth

export const newsState = {
  items: [],
  index: 0,
};

export function setNewsItems(items) {
  newsState.items = Array.isArray(items) ? items : [];
  newsState.index = 0;
}

export function getCurrentNews() {
  if (!newsState.items.length) return null;
  return newsState.items[newsState.index];
}

export function moveNext() {
  if (!newsState.items.length) return null;
  if (newsState.index < newsState.items.length - 1) {
    newsState.index += 1;
  }
  return getCurrentNews();
}

export function movePrev() {
  if (!newsState.items.length) return null;
  if (newsState.index > 0) {
    newsState.index -= 1;
  }
  return getCurrentNews();
}
