// static/js/api.js

const BASE_URL = "";

// ఒక్క న్యూస్ తెచ్చే API
export async function fetchNews(direction = "current") {
  const url =
    direction === "current"
      ? "/news"
      : `/news?direction=${encodeURIComponent(direction)}`;

  const res = await fetch(url, {
    method: "GET",
    headers: {
      "Accept": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch news: ${res.status}`);
  }

  return await res.json(); // { id, title, summary, link, likes, dislikes }
}

// లైక్ / డిస్‌లైక్ API
export async function sendReaction(newsId, type) {
  const res = await fetch(`/news/${encodeURIComponent(newsId)}/reaction`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({ type }), // "like" | "dislike"
  });

  if (!res.ok) {
    throw new Error(`Failed to send reaction: ${res.status}`);
  }

  return await res.json(); // కొత్త counts తో ఉన్న news object వస్తుందని assume చేస్తున్నాం
}

// కామెంట్ పంపడం (ఇంకా backend లో లేకపోయినా safe)
export async function sendComment(newsId, text) {
  const res = await fetch(`/news/${encodeURIComponent(newsId)}/comment`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json",
    },
    body: JSON.stringify({ text }),
  });

  if (!res.ok) {
    throw new Error(`Failed to send comment: ${res.status}`);
  }

  return await res.json();
}
