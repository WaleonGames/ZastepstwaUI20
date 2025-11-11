document.addEventListener("keydown", (e) => {
  // 🔹 wykrycie kombinacji Win + H
  if ((e.metaKey || e.key === "Meta" || e.key === "OS" || e.key === "Win") && e.code === "KeyH") {
    e.preventDefault();
    console.log("🚀 [HOTKEY] Win+H → /activate-terminal");

    // przekierowanie do aktywatora terminala
    window.location.href = "/activate-terminal";
  }
});
