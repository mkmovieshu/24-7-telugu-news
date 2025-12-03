// static/js/api.js

// API helper functions

// base URL అవసరం లేదు, same origin నుంచి కాల్ చేస్తున్నాం
// ఇక్కడ future లో versioning వంటివి add చేయొచ్చు
const BASE_URL = "";

// ఒక్క న్యూస్ తెచ్చే API
export async function fetchNews(direction = "current") {
  const url =
    direction === "current"
      ? `${BASE_URL}/news`
      : `${BASE_URL}/news?direction=${encodeURIComponent(direction)}`;

  const res = await fetch(url, {
    method: "GET",
    headers: {
      Accept: "application/json",
    },
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch news: ${res.status}`);
  }

  const data = await res.json();
  // ⚠️ backend కొన్నిసార్లు list పంపుతున్నట్టు కనిపిస్తోంది
  // UI కి ఒక్క item కావాలి కాబట్టి మొదటి item తీసుకుంటాం
  if (Array.isArray(data)) {
    return data[0] || null;
  }
  return data; // ఒక్క object అయితే direct గా
}

// లైక్ / డిస్‌లైక్ API
export async function sendReaction(newsId, type) {
  const res = await fetch(
    `${BASE_URL}/news/${encodeURIComponent(newsId)}/reaction`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ type }), // "like" | "dislike"
    }
  );

  if (!res.ok) {
    throw new Error(`Failed to send reaction: ${res.status}`);
  }

  // updated news object వస్తుందని assume చేస్తున్నాం
  return await res.json();
}

// కామెంట్ పంపడం (future use)
export async function sendComment(newsId, text) {
  const res = await fetch(
    `${BASE_URL}/news/${encodeURIComponent(newsId)}/comment`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ text }),
    }
  );

  if (!res.ok) {
    throw new Error(`Failed to send comment: ${res.status}`);
  }

  return await res.json();
}
