// Comment System (simple version)
// ---------------------------------------------

let commentsBoxVisible = false;

// HTML template for a single comment
function renderComment(c) {
    return `
        <div class="comment-item">
            <div class="comment-user">👤 ${c.user || "User"}</div>
            <div class="comment-text">${c.text}</div>
        </div>
    `;
}

// Load comments for a news item
async function loadComments(newsId) {
    try {
        const res = await fetch(`/api/comments/${newsId}`);
        if (!res.ok) throw new Error("Failed to load comments");

        const data = await res.json();
        const list = document.getElementById("comments-list");

        if (!list) return;

        list.innerHTML = data.comments.map(renderComment).join("");
    } catch (err) {
        console.error("COMMENTS LOAD ERROR:", err);
    }
}

// Submit new comment
async function submitComment(newsId) {
    const input = document.getElementById("comment-input");
    const text = input.value.trim();

    if (!text) return;

    try {
        const res = await fetch(`/api/comments/${newsId}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ text })
        });

        if (!res.ok) throw new Error("Failed to submit comment");

        input.value = "";
        await loadComments(newsId);
    } catch (err) {
        console.error("COMMENT SUBMIT ERROR:", err);
    }
}

// Toggle comment box
function toggleComments(newsId) {
    const box = document.getElementById("comments-box");

    if (!box) return;

    commentsBoxVisible = !commentsBoxVisible;

    if (commentsBoxVisible) {
        box.style.display = "block";
        loadComments(newsId);
    } else {
        box.style.display = "none";
    }
}
