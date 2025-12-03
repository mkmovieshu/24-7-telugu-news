// static/js/api.js
// All API calls in one place

const API_BASE = ""; // same origin

async function apiRequest(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${path} failed: ${res.status} ${text}`);
  }

  return res.headers.get("content-type")?.includes("application/json")
    ? res.json()
    : res.text();
}

// --- public functions ---

window.fetchNewsItem = async function fetchNewsItem(direction) {
  // direction: undefined | "next" | "prev"
  const query = direction ? `?direction=${encodeURIComponent(direction)}` : "";
  return apiRequest(`/news${query}`);
};

window.sendReaction = async function sendReaction(newsId, reaction) {
  if (!newsId) return;

  return apiRequest(`/news/${encodeURIComponent(newsId)}/reaction`, {
    method: "POST",
    body: JSON.stringify({ reaction }), // "like" | "dislike"
  });
};

window.sendComment = async function sendComment(newsId, text) {
  if (!newsId || !text?.trim()) return;

  return apiRequest(`/news/${encodeURIComponent(newsId)}/comment`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
};
