// Rendering + animation logic for news card

(function () {
  function setCardContent(news) {
    const titleEl = document.getElementById("news-title");
    const summaryEl = document.getElementById("news-summary");
    const moreInfoBtn = document.getElementById("more-info-btn");
    const likeCountEl = document.getElementById("like-count");
    const dislikeCountEl = document.getElementById("dislike-count");

    titleEl.textContent = news.title || "";
    summaryEl.textContent = news.summary || "";

    if (news.link) {
      moreInfoBtn.href = news.link;
      moreInfoBtn.style.display = "block";
    } else {
      moreInfoBtn.href = "#";
      moreInfoBtn.style.display = "none";
    }

    likeCountEl.textContent = news.likes ?? 0;
    dislikeCountEl.textContent = news.dislikes ?? 0;

    // store id on buttons for reactions/comments
    document.getElementById("like-btn").dataset.id = news.id;
    document.getElementById("dislike-btn").dataset.id = news.id;
    document.getElementById("comment-input").dataset.id = news.id;
  }

  async function renderNews(news, direction) {
    const card = document.getElementById("news-card");
    if (!card) return;

    if (!direction) {
      // first render, no animation
      setCardContent(news);
      window.NewsState.current = news;
      return;
    }

    if (window.NewsState.isAnimating) return;
    window.NewsState.isAnimating = true;

    const outClass =
      direction === "next" ? "flip-out-up" : "flip-out-down";
    const inClass = direction === "next" ? "flip-in-up" : "flip-in-down";

    // Step 1: play flip-out
    card.classList.remove("flip-in-up", "flip-in-down");
    card.classList.add(outClass);

    function onOutEnd(e) {
      if (e.target !== card) return;
      card.removeEventListener("animationend", onOutEnd);
      card.classList.remove(outClass);

      // Step 2: change content, then flip-in
      setCardContent(news);
      card.classList.add(inClass);

      card.addEventListener("animationend", function onInEnd(ev) {
        if (ev.target !== card) return;
        card.removeEventListener("animationend", onInEnd);
        card.classList.remove(inClass);
        window.NewsState.isAnimating = false;
      });
    }

    card.addEventListener("animationend", onOutEnd);
    window.NewsState.current = news;
  }

  window.Render = {
    renderNews,
  };
})();
