export async function fetchNews() {
    const res = await fetch("/news?limit=100");
    return res.json();
}

export async function fetchComments(id) {
    const res = await fetch(`/news/${id}/comments`);
    return res.json();
}

export async function postComment(id, text) {
    const res = await fetch(`/news/${id}/comments`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
    });
    return res.json();
}

export async function postReaction(id, action) {
    const res = await fetch(`/news/${id}/reaction`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }),
    });
    return res.json();
}
