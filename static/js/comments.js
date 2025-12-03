// static/js/comments.js
// Simple comment form handler

window.setupComments = function setupComments() {
  const form = document.getElementById("comment-form");
  const input = document.getElementById("comment-input");

  if (!form || !input) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    const item = window.getCurrentNews();
    if (!item) return;

    const newsId = item.id || item._id;
    if (!newsId) return;

    try {
      await window.sendComment(newsId, text);
      input.value = "";
      alert("మీ కామెంట్ సేవ్ చేయబడింది. ధన్యవాదాలు!");
    } catch (err) {
      console.error(err);
      alert("కామెంట్ సేవ్ కాలేదు. తర్వాత ప్రయత్నించండి.");
    }
  });
};
