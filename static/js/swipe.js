// static/js/swipe.js
import { fetchNews, postReaction } from './api.js';
import { loadCommentsForCurrent, postCommentForCurrent } from './comments.js';

let state = { items: [], idx: 0 };

export async function initSwipe(limit = 50) {
  try {
    const data = await fetchNews(limit);
    state.items = (data && data.items) || [];
    state.idx = 0;
    if (state.items.length === 0) {
      showEmpty();
      return;
    }
    showIndex(0);
  } catch (err) {
    console.error('initSwipe error', err);
    showError(err.message);
  }
}

function showEmpty() {
  const title = document.getElementById('news-title');
  const summary = document.getElementById('news-summary');
  if (title) title.textContent = 'టైటిల్ లేదు';
  if (summary) summary.textContent = 'న్యూస్ లోడ్ అవ్వలేదు...';
  const likes = document.getElementById('news-likes');
  if (likes) likes.textContent = '0';
  document.getElementById('comments')?.innerHTML = '';
}

function showError(msg) {
  showEmpty();
  console.error('showError', msg);
}

function showIndex(i) {
  if (!state.items || state.items.length === 0) return showEmpty();
  if (i < 0) i = 0;
  if (i >= state.items.length) i = state.items.length - 1;
  state.idx = i;
  const it = state.items[i] || {};
  document.getElementById('news-title').textContent = it.title || 'టైటిల్ లేదు';
  document.getElementById('news-summary').textContent = it.summary || '';
  const likesEl = document.getElementById('news-likes');
  if (likesEl) likesEl.textContent = it.likes ?? 0;
  const dislikesEl = document.getElementById('news-dislikes');
  if (dislikesEl) dislikesEl.textContent = it.dislikes ?? 0;

  // load comments for this news id
  if (it.id) loadCommentsForCurrent(it.id);
}

export function next() { showIndex(state.idx + 1); }
export function prev() { showIndex(state.idx - 1); }

export async function likeCurrent() {
  const it = state.items[state.idx];
  if (!it || !it.id) return;
  try {
    const res = await postReaction(it.id, 'like');
    // update local state and UI
    it.likes = res.likes ?? it.likes;
    document.getElementById('news-likes').textContent = it.likes ?? 0;
  } catch (err) {
    console.error(err);
    alert('Like failed: ' + err.message);
  }
}

export async function dislikeCurrent() {
  const it = state.items[state.idx];
  if (!it || !it.id) return;
  try {
    const res = await postReaction(it.id, 'dislike');
    it.dislikes = res.dislikes ?? it.dislikes;
    document.getElementById('news-dislikes').textContent = it.dislikes ?? 0;
  } catch (err) {
    console.error(err);
    alert('Dislike failed: ' + err.message);
  }
}

// expose simple init for HTML to call
window.appSwipe = { initSwipe, next, prev, likeCurrent, dislikeCurrent, postCommentForCurrent };
