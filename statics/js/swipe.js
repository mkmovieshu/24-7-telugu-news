// Simple swipe + fetch logic
const newsRoot = document.getElementById("news-root");
let isLoading = false;

async function loadNews(direction = null) {
    if (isLoading) return;
    isLoading = true;

    try {
        const params = direction ? `?direction=${direction}` : "";
        const res = await fetch(`/news${params}`);
        if (!res.ok) {
            throw new Error("Failed to load news");
        }

        const html = await res.text();
        newsRoot.innerHTML = html;

        // కొత్త కార్డ్‌కి flip / slide animation autoగా run అవుతుంది
        // ఎందుకంటే CSS లో .news-card కి animation set చేశాం
    } catch (err) {
        console.error(err);
        newsRoot.innerHTML = `
            <div class="news-card">
                <div class="news-body">
                    <h2 class="news-title">న్యూస్ లోడ్ కాలేదు</h2>
                    <p class="news-summary">
                        నెట్ కనెక్షన్ చెక్ చేసి, మళ్లీ కొంచెం సేపటి తర్వాత ప్రయత్నించండి.
                    </p>
                </div>
            </div>
        `;
    } finally {
        isLoading = false;
    }
}

function setupSwipe() {
    let startY = null;
    const SWIPE_THRESHOLD = 40;

    document.addEventListener("touchstart", (e) => {
        if (e.touches.length === 1) {
            startY = e.touches[0].clientY;
        }
    });

    document.addEventListener("touchend", (e) => {
        if (startY === null) return;
        const endY = e.changedTouches[0].clientY;
        const deltaY = startY - endY;

        if (deltaY > SWIPE_THRESHOLD) {
            // swipe up -> next
            loadNews("next");
        } else if (deltaY < -SWIPE_THRESHOLD) {
            // swipe down -> previous
            loadNews("prev");
        }

        startY = null;
    });

    // Mouse wheel support (mobile కాకుండా for testing)
    let wheelTimeout;
    window.addEventListener("wheel", (e) => {
        clearTimeout(wheelTimeout);
        wheelTimeout = setTimeout(() => {
            if (e.deltaY > 0) {
                loadNews("next");
            } else if (e.deltaY < 0) {
                loadNews("prev");
            }
        }, 60);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    loadNews();      // మొదటి న్యూస్
    setupSwipe();    // swipe handlers
});
