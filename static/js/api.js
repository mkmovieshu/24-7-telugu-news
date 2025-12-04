// static/js/api.js
// Backend API helpers (with compatibility exports for other modules)

async function _fetchJson(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text().catch(()=>"");
    const err = new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
    err.status = res.status;
    throw err;
  }
  return res.json().catch(()=>null);
}

export async function fetchNewsList() {
  const data = await _fetchJson("/news");
  return data && data.items ? data.items : [];
}

// old name compatibility (if some module expects fetchNews)
export const fetchNews = fetchNewsList;

export async function sendReaction(newsId, action) {
  return await _fetchJson(`/news/${newsId}/reaction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
}

export async function fetchComments(newsId) {
  const data = await _fetchJson(`/news/${newsId}/comments`);
  return data && data.items ? data.items : [];
}

export async function sendComment(newsId, text) {
  return await _fetchJson(`/news/${newsId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

/*
  Compatibility / wrapper exports:
  Some other frontend modules expect these names:
    - loadCommentsForCurrent
    - postComment
    - postReaction (maybe)
  We export them so existing imports keep working.
*/

export async function loadCommentsForCurrent(newsId) {
  // returns array of comment objects
  return await fetchComments(newsId);
}

export async function postComment(newsId, text) {
  // returns { id: "<inserted_id>" } or throws
  return await sendComment(newsId, text);
}

export async function postReaction(newsId, action) {
  // existing sendReaction returns likes/dislikes; wrapper name
  return await sendReaction(newsId, action);
}
