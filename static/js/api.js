// Backend API helpers
// (slim wrapper around your FastAPI endpoints)

export async function fetchNewsList() {
  console.log("[api] fetchNewsList()");
  const res = await fetch("/news");
  if (!res.ok) {
    console.error("[api] fetchNewsList failed", res.status);
    throw new Error("Failed to load news");
  }
  const data = await res.json();
  return data.items || [];
}

export async function sendReaction(newsId, action) {
  console.log("[api] sendReaction", newsId, action);
  const res = await fetch(`/news/${newsId}/reaction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  if (!res.ok) {
    const text = await res.text().catch(()=>"");
    console.error("[api] sendReaction failed", res.status, text);
    throw new Error("Reaction failed");
  }
  return await res.json();
}

export async function fetchComments(newsId) {
  console.log("[api] fetchComments", newsId);
  const res = await fetch(`/news/${newsId}/comments`);
  if (!res.ok) {
    console.error("[api] fetchComments failed", res.status);
    throw new Error("Failed to load comments");
  }
  const data = await res.json();
  return data.items || [];
}

export async function sendComment(newsId, text) {
  console.log("[api] sendComment", newsId, text);
  const res = await fetch(`/news/${newsId}/comments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    const txt = await res.text().catch(()=>"");
    console.error("[api] sendComment failed", res.status, txt);
    throw new Error("Failed to save comment");
  }
  return await res.json();
}
