// state.js
export const state = {
  items: [],
  currentIndex: 0,
  likes: {}, // id -> { like: number, dislike: number, my: 'like' | 'dislike' | null }
  comments: {} // id -> string[]
};

export function setItems(items) {
  state.items = items || [];
  state.currentIndex = 0;
}

export function getItems() {
  return state.items;
}

export function getCurrentIndex() {
  return state.currentIndex;
}

export function setCurrentIndex(idx) {
  if (idx < 0 || idx >= state.items.length) return;
  state.currentIndex = idx;
}

export function next() {
  if (state.currentIndex < state.items.length - 1) {
    state.currentIndex += 1;
    return true;
  }
  return false;
}

export function prev() {
  if (state.currentIndex > 0) {
    state.currentIndex -= 1;
    return true;
  }
  return false;
}

export function getItemId(item, index) {
  return (
    item.id ||
    item._id ||
    item.original_link ||
    item.link ||
    item.url ||
    `idx-${index}`
  );
}

export function getReactions(id) {
  if (!state.likes[id]) {
    state.likes[id] = { like: 0, dislike: 0, my: null };
  }
  return state.likes[id];
}

export function setReaction(id, type) {
  const rec = getReactions(id);
  if (rec.my === type) {
    // toggle off
    rec.my = null;
    if (type === "like" && rec.like > 0) rec.like--;
    if (type === "dislike" && rec.dislike > 0) rec.dislike--;
  } else {
    if (type === "like") {
      rec.like++;
      if (rec.my === "dislike" && rec.dislike > 0) rec.dislike--;
    } else if (type === "dislike") {
      rec.dislike++;
      if (rec.my === "like" && rec.like > 0) rec.like--;
    }
    rec.my = type;
  }
}

export function getComments(id) {
  if (!state.comments[id]) {
    state.comments[id] = [];
  }
  return state.comments[id];
}

export function addComment(id, text) {
  const trimmed = text.trim();
  if (!trimmed) return;
  getComments(id).push(trimmed);
}
