// ==========================
// Swipe Handler v2.0
// ==========================

import { state } from "./state.js";
import { renderNews } from "./render.js";

const newsCard = document.getElementById("news-card");

// Swipe gesture values
let startY = 0;
let currentY = 0;
const SWIPE_THRESHOLD = 60;     // minimum distance (px) to count as swipe
const ANIM_DURATION = 250;      // ms
let isAnimating = false;

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

// --------------------------
// Low-level handlers
// --------------------------

function onStart(y) {
    startY = y;
    currentY = y;
}

function onMove(y) {
    currentY = y;
}

async function onEnd() {
    if (!startY && !currentY) return;

    const diff = startY - currentY;

    // reset for next swipe
    startY = 0;
    currentY = 0;

    if (Math.abs(diff) < SWIPE_THRESHOLD) {
        // not enough movement → ignore
        return;
    }

    if (diff > 0) {
        // swipe UP → next news
        await goTo("next");
    } else {
        // swipe DOWN → previous news
        await goTo("prev");
    }
}

// --------------------------
// Change current news + animation
// --------------------------

async function goTo(direction) {
    if (!newsCard) return;
    if (!state.news || state.news.length === 0) return;
    if (isAnimating) return;

    let nextIndex = state.currentIndex ?? 0;

    if (direction === "next") {
        if (nextIndex >= state.news.length - 1) {
            // already at last item
            return;
        }
        nextIndex += 1;
    } else if (direction === "prev") {
        if (nextIndex <= 0) {
            // already at first item
            return;
        }
        nextIndex -= 1;
    }

    isAnimating = true;

    // Remove any previous animation classes
    newsCard.classList.remove("swipe-up", "swipe-down", "swipe-reset");
    // Force reflow so animation retriggers
    void newsCard.offsetWidth;

    // First phase: slide old card out
    newsCard.classList.add(direction === "next" ? "swipe-up" : "swipe-down");
    await sleep(ANIM_DURATION);

    // Update index + re-render with NEW data
    state.currentIndex = nextIndex;
    renderNews();

    // Second phase: small reset animation for new card
    newsCard.classList.remove("swipe-up", "swipe-down");
    newsCard.classList.add("swipe-reset");
    await sleep(ANIM_DURATION);

    newsCard.classList.remove("swipe-reset");
    isAnimating = false;
}

// --------------------------
// Attach listeners
// --------------------------

if (newsCard) {
    // Touch (mobile)
    newsCard.addEventListener(
        "touchstart",
        (e) => {
            if (!e.touches || e.touches.length === 0) return;
            onStart(e.touches[0].clientY);
        },
        { passive: true }
    );

    newsCard.addEventListener(
        "touchmove",
        (e) => {
            if (!e.touches || e.touches.length === 0) return;
            onMove(e.touches[0].clientY);
        },
        { passive: true }
    );

    newsCard.addEventListener(
        "touchend",
        () => {
            onEnd();
        },
        { passive: true }
    );

    // Mouse (browser testing)
    newsCard.addEventListener("mousedown", (e) => {
        onStart(e.clientY);
    });

    newsCard.addEventListener("mousemove", (e) => {
        if (e.buttons !== 1) return;
        onMove(e.clientY);
    });

    newsCard.addEventListener("mouseup", () => {
        onEnd();
    });
}

// make this an ES module
export {};
