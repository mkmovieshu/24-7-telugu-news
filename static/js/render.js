// static/js/render.js
// Replace your existing render.js with this file
// Assumes you're including JS modules: <script type="module" src="/static/js/render.js"></script>

import { setNewsItems, getCurrentNews, moveNext, movePrev } from './state.js';
import { fetchNews } from './api.js';

const safeText = (el, text) => { if (!el) return; el.textContent = text ?? ''; };
const safeAttr = (el, attr, val) => { if (!el) return; if (val === null || val === undefined) el.removeAttribute(attr); else el.setAttribute(attr, val); };

export async function initAndRender(limit = 100) {
  try {
    const res = await fetchNews(limit); // expects { items: [...] }
    if (!res || !Array.isArray(res.items)) {
      console.warn('render.js: fetchNews returned unexpected data', res);
      return;
    }
    setNewsItems(res.items);
    renderCurrent();
  } catch (err) {
    console.error('render.initAndRender error', err);
    showAlert('Failed loading news: ' + (err.message || err));
  }
}

export function renderCurrent() {
  const news = getCurrentNews();
  // fallback elements — ensure these IDs exist in your app.html
  const titleEl = document.getElementById('news-title');
  const summaryEl = document.getElementById('news-summary');
  const linkEl = document.getElementById('news-link');
  const imgEl = document.getElementById('news-image');
  const likeEl = document.getElementById('like-count');
  const dislikeEl = document.getElementById('dislike-count');

  if (!news) {
    // show "no news" state
    safeText(titleEl, 'No news available');
    safeText(summaryEl, '');
    safeAttr(linkEl, 'href', '#');
    if (imgEl) imgEl.style.display = 'none';
    safeText(likeEl, '0');
    safeText(dislikeEl, '0');
    return;
  }

  // Use properties present in backend items (title, summary, link, image, likes)
  safeText(titleEl, news.title || news.headline || '');
  safeText(summaryEl, news.summary || news.excerpt || news.description || '');
  safeAttr(linkEl, 'href', news.link || news.url || '#');
  if (imgEl) {
    const imgSrc = news.image || news.thumbnail || news.media || null;
    if (imgSrc) {
      imgEl.style.display = '';
      imgEl.src = imgSrc;
    } else {
      imgEl.style.display = 'none';
    }
  }
  safeText(likeEl, String(news.likes || 0));
  safeText(dislikeEl, String(news.dislikes || 0));
}

export function nextNews() {
  const n = moveNext();
  if (n) renderCurrent();
  return n;
}

export function prevNews() {
  const n = movePrev();
  if (n) renderCurrent();
  return n;
}

// optional visible alert box for errors (non-blocking)
function showAlert(msg) {
  let box = document.getElementById('notification-box');
  if (!box) {
    box = document.createElement('div');
    box.id = 'notification-box';
    Object.assign(box.style, {
      position: 'fixed',
      top: '12px',
      left: '12px',
      right: '12px',
      zIndex: 99999,
      background: '#222',
      color: '#fff',
      padding: '8px 12px',
      borderRadius: '6px',
      opacity: '0.95',
      fontSize: '14px'
    });
    document.body.appendChild(box);
  }
  box.textContent = msg;
  setTimeout(() => { if (box) box.remove(); }, 3500);
}

// auto-init on load
window.addEventListener('DOMContentLoaded', () => {
  // start fetch + render
  initAndRender(100);
});
