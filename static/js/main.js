// Entry point – load first news, wire swipe + keyboard

(function () {
  const card = document.getElementById("news-card");

  async function loadNews(direction) {
    try {
      const data = await Api.getNews(direction);
      // API returns single object {id,title,summary,link,likes,dislikes}
      await Render.renderNews(data, direction);
    } catch (err) {
      console.error("Failed to load news", err);
      document.getElementById("news-title").textContent =
        "న్యూస్ లోడ్ అవ్వడంలో సమస్య వచ్చింది.";
      document.getElementById("news-summary").textContent =
        "కొన్ని సెకండ్లు తర్వాత మళ్లీ ప్రయత్నించండి.";
    }
  }

  function setupSwipe() {
    Swipe.setupSwipe(card, (direction) => {
      if (direction === "next") {
        loadNews("next");
      } else if (direction === "prev") {
        loadNews("prev");
      }
    });
  }

  function setupKeyboard() {
    // Up/Down arrows for desktop
    window.addEventListener("keydown", (e) => {
      if (e.key === "ArrowUp") {
        loadNews("next");
      } else if (e.key === "ArrowDown") {
        loadNews("prev");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    loadNews(null); // first item
    setupSwipe();
    setupKeyboard();
  });
})();
