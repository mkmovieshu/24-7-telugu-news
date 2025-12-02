let startY = 0;

document.addEventListener("touchstart", e => {
    startY = e.touches[0].clientY;
});

document.addEventListener("touchend", e => {
    let endY = e.changedTouches[0].clientY;
    let diff = startY - endY;

    if (diff > 70) {
        window.location.href = "/news/next";
    } 
    else if (diff < -70) {
        window.location.href = "/news/prev";
    }
});
