// "Fake" comments – only saved locally on device

(function () {
  const input = document.getElementById("comment-input");
  const btn = document.getElementById("comment-save-btn");
  const statusEl = document.getElementById("comment-status");

  function showStatus(text) {
    statusEl.textContent = text;
    if (!text) return;
    setTimeout(() => {
      statusEl.textContent = "";
    }, 2000);
  }

  async function handleSave() {
    const id = input.dataset.id;
    const text = (input.value || "").trim();
    if (!id || !text) {
      showStatus("కామెంట్ టైప్ చేయండి.");
      return;
    }

    try {
      await Api.saveCommentLocally(id, text);
      input.value = "";
      showStatus("కామెంట్ ఈ ఫోన్లో సేవ్ అయింది.");
    } catch {
      showStatus("కామెంట్ సేవ్ కాలేదు.");
    }
  }

  if (btn && input) {
    btn.addEventListener("click", handleSave);
  }
})();
