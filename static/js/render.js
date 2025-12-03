// ===============================
// RENDER NEWS ITEM TO UI
// ===============================

export function renderNews(item) {
    const card = document.getElementById("news-card");
    const title = document.getElementById("news-title");
    const summary = document.getElementById("news-summary");
    const linkBtn = document.getElementById("news-link");
    const likeCount = document.getElementById("like-count");
    const dislikeCount = document.getElementById("dislike-count");

    if (!item) {
        title.innerText = "Loading...";
        summary.innerText = "న్యూస్ లోడ్ అవుతోంది...";
        linkBtn.href = "#";
        return;
    }

    // Update content
    title.innerText = item.title || "No title";
    summary.innerText = item.summary || "No summary";
    linkBtn.href = item.link || "#";

    // Update counts
    likeCount.innerText = item.likes ?? 0;
    dislikeCount.innerText = item.dislikes ?? 0;

    // Animation
    card.classList.remove("fade-in");
    void card.offsetWidth;  // restart animation
    card.classList.add("fade-in");
}
