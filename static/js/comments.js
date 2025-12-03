// static/js/comments.js

export function initComments() {
  const input = document.getElementById("comment-input");
  const button = document.getElementById("comment-submit");
  const note = document.getElementById("comment-note");

  if (!input || !button) {
    console.warn("initComments: elements missing");
    return;
  }

  button.addEventListener("click", () => {
    const text = input.value.trim();
    if (!text) return;

    // For now, just clear and show small note. Later → call API.
    input.value = "";
    if (note) {
      note.textContent = "కామెంట్ సేవ్ చేయబడింది (డెవలప్‌మెంట్ మోడ్).";
    }
  });
}
