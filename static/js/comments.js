// static/js/comments.js
import { fetchComments, postComment } from './api.js';

// container id where comments will be rendered: ensure app.html has <div id="comments"></div>
export async function loadCommentsForCurrent(newsId) {
  const container = document.getElementById('comments');
  if (!container) return;
  container.innerHTML = 'Loading comments...';

  try {
    const data = await fetchComments(newsId);
    container.innerHTML = '';
    if (!data || !Array.isArray(data.items) || data.items.length === 0) {
      container.innerHTML = '<div class="no-comments">కామెంట్స్ లేవు</div>';
      return;
    }
    data.items.forEach(c => {
      const el = document.createElement('div');
      el.className = 'comment-item';
      const when = c.created_at ? new Date(c.created_at).toLocaleString() : '';
      el.innerHTML = `<div class="comment-text">${escapeHtml(c.text)}</div><div class="comment-meta">${when}</div>`;
      container.appendChild(el);
    });
  } catch (err) {
    container.innerHTML = `<div class="error">Comments error: ${escapeHtml(err.message)}</div>`;
    console.error(err);
  }
}

export async function postCommentForCurrent(newsId, text) {
  text = (text || '').trim();
  if (!text) return;
  try {
    const res = await postComment(newsId, text);
    // res contains new id; reload comments
    await loadCommentsForCurrent(newsId);
    return res;
  } catch (err) {
    console.error('postCommentForCurrent error', err);
    alert('Comment failed: ' + err.message);
    throw err;
  }
}

// small helper
function escapeHtml(s) {
  return String(s || '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}
