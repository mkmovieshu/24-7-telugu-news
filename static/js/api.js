// static/js/api.js
export async function fetchNewsList(limit = 100) {
  const url = `/news?limit=${limit}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("failed to fetch news");
  return res.json();
}

export async function postReaction(itemId, type = "like") {
  const url = `/likes/${itemId}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type })
  });
  if (!res.ok) return false;
  return res.json();
}

export async function postComment(itemId, text) {
  const url = `/comments/${itemId}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  });
  return res.json();
}
