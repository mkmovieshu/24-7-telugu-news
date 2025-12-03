// Like / Dislike behaviour with local immediate update

(function () {
  const likeBtn = document.getElementById("like-btn");
  const dislikeBtn = document.getElementById("dislike-btn");
  const likeCountEl = document.getElementById("like-count");
  const dislikeCountEl = document.getElementById("dislike-count");

  function updateButtonStates(active) {
    likeBtn.classList.toggle("active", active === "like");
    dislikeBtn.classList.toggle("active", active === "dislike");
  }

  async function handleReaction(type) {
    const id = (type === "like" ? likeBtn : dislikeBtn).dataset.id;
    if (!id) return;

    const likeCount = parseInt(likeCountEl.textContent || "0", 10);
    const dislikeCount = parseInt(dislikeCountEl.textContent || "0", 10);

    if (type === "like") {
      likeCountEl.textContent = likeCount + 1;
      updateButtonStates("like");
    } else {
      dislikeCountEl.textContent = dislikeCount + 1;
      updateButtonStates("dislike");
    }

    // fire-and-forget backend call (if implemented)
    Api.sendReaction(id, type).catch(() => {});
  }

  if (likeBtn && dislikeBtn) {
    likeBtn.addEventListener("click", () => handleReaction("like"));
    dislikeBtn.addEventListener("click", () => handleReaction("dislike"));
  }
})();
