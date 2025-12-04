// static/js/api.js
// simple ES module with named exports used by other modules

export async function fetchNews(limit = 50) {
  const res = await fetch(`/news?limit=${encodeURIComponent(limit)}`);
  if (!res.ok) throw new Error(`fetchNews failed: ${res.status}`);
  return res.json();
}

export async function postReaction(newsId, action) {
  const res = await fetch(`/news/${newsId}/reaction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action })
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`postReaction failed ${res.status}: ${text}`);
  }
  return res.json();
}

export async function fetchComments(newsId) {
  const res = await fetch(`/news/${newsId}/comments`);
  if (!res.ok) throw new Error(`fetchComments failed: ${res.status}`);
  return res.json();
}

export async function postComment(newsId, text) {
  const res = await fetch(`/news/${newsId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  if (!res.ok) {
    const textBody = await res.text();
    throw new Error(`postComment failed ${res.status}: ${textBody}`);
  }
  return res.json();
}
