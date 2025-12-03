// static/js/api.js

// ---- Helpers ----
function normalizeNewsItem(raw) {
  if (!raw) return null;

  const id =
    raw.id ||
    raw._id ||
    (raw._id && raw._id.$oid) ||
    null;

  return {
    id,
    title: raw.title || "శీర్షిక అందుబాటులో లేదు",
    summary: raw.summary || "సంక్షిప్త సమాచారం అందుబాటులో లేదు.",
    link: raw.link || "#",
    likes: typeof raw.likes === "number" ? raw.likes : 0,
    dislikes: typeof raw.dislikes === "number" ? raw.dislikes : 0,
  };
}

// ---- API wrappers ----
export async function fetchNews(direction = null) {
  try {
    let url = "/news";
    if (direction === "next" || direction === "prev") {
      url += `?direction=${direction}`;
    }

    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`Failed to fetch news: ${res.status}`);
    }

    const data = await res.json();

    // Backend currently returns *array* of docs → take first item
    let item = null;

    if (Array.isArray(data)) {
      item = data.length > 0 ? data[0] : null;
    } else if (data && Array.isArray(data.items)) {
      item = data.items[0] || null;
    } else if (data && typeof data === "object") {
      // single object case
      item = data;
    }

    return normalizeNewsItem(item);
  } catch (err) {
    console.error("fetchNews error:", err);
    return null;
  }
}

export async function sendReaction(newsId, type) {
  if (!newsId) {
    console.warn("sendReaction: newsId missing");
    return null;
  }

  try {
    const res = await fetch(`/news/${newsId}/reaction`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ type }),
    });

    if (!res.ok) {
      throw new Error(`Reaction failed: ${res.status}`);
    }

    const data = await res.json();

    // Backend should return updated counts; but బెస్ట్‌ – normalize చేసి రిటర్న్
    return {
      likes: typeof data.likes === "number" ? data.likes : undefined,
      dislikes: typeof data.dislikes === "number" ? data.dislikes : undefined,
    };
  } catch (err) {
    console.error("sendReaction error:", err);
    return null;
  }
}
