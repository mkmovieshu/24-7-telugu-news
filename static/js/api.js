// Backend API helpers

export async function fetchNewsList() {
  const res = await fetch("/news");
  if (!res.ok) {
    throw new Error("Failed to load news");
  }
  const data = await res.json();
  return data.items || [];
}

export async function sendReaction(newsId, action) {
  const res = await fetch(`/news/${newsId}/reaction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!res.ok) {
    throw new Error("Reaction failed");
  }
  return await res.json();
}

export async function fetchComments(newsId) {
  const res = await fetch(`/news/${newsId}/comments`);
  if (!res.ok) throw new Error("Failed to load comments");
  const data = await res.json();
  return data.items || [];
}

export async function sendComment(newsId, text) {
  const res = await fetch(`/news/${newsId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Failed to save comment");
  return await res.json();
}
