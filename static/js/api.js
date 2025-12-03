// Basic API wrapper – only JSON, no UI here
window.Api = (function () {
  async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
      },
      ...options,
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return res.json();
  }

  async function getNews(direction) {
    const url = direction ? `/news?direction=${direction}` : "/news";
    return fetchJson(url);
  }

  async function sendReaction(id, type) {
    // optional – if backend has endpoint
    try {
      await fetchJson(`/news/${id}/reaction`, {
        method: "POST",
        body: JSON.stringify({ type }),
      });
    } catch {
      // ignore errors for now
    }
  }

  async function saveCommentLocally(id, text) {
    // Only localStorage – no backend call
    if (!id) return;
    const key = `news_comments_${id}`;
    const list = JSON.parse(localStorage.getItem(key) || "[]");
    list.unshift({
      text,
      createdAt: Date.now(),
    });
    localStorage.setItem(key, JSON.stringify(list.slice(0, 20)));
  }

  return {
    getNews,
    sendReaction,
    saveCommentLocally,
  };
})();
