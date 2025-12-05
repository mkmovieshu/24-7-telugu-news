import { getCurrentNews } from "./state.js";

export function renderNews() {
    const container = document.getElementById("news-container");
    const item = getCurrentNews();

    if (!item) {
        container.innerHTML = "<p>No news available</p>";
        return;
    }

    container.innerHTML = `
        <div class="news-card">
            <h2>${item.title}</h2>
            <p>${item.summary}</p>
            <a href="${item.link}" target="_blank">Read More</a>

            <div class="reaction-row">
                <button class="like-btn">👍 ${item.likes}</button>
                <button class="dislike-btn">👎 ${item.dislikes}</button>
            </div>
        </div>
    `;
}
