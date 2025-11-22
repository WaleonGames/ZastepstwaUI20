/* ================================
 *  ⏰ ZEGAR
 * ================================ */
function updateClock(dateFormat = "horizontal") {
  const now = new Date();

  const h = now.getHours().toString().padStart(2, "0");
  const m = now.getMinutes().toString().padStart(2, "0");

  const d = now.getDate().toString().padStart(2, "0");
  const mo = (now.getMonth() + 1).toString().padStart(2, "0");
  const y = now.getFullYear();

  const timeEl = document.getElementById("footer-time");
  const dateEl = document.getElementById("footer-date");

  if (!timeEl || !dateEl) return;

  timeEl.textContent = `${h}:${m}`;

  // format poziomy → 21.11.2025
  // format pionowy  → 21•11•2025 (ładny, kompaktowy)
  if (dateFormat === "vertical") {
    dateEl.textContent = `${d}.${mo}.${y}`;
  } else {
    dateEl.textContent = `${d}.${mo}.${y}`;
  }
}

setInterval(updateClock, 1000);
updateClock();


/* ================================
 *  📂 PANEL KALENDARZA
 * ================================ */
document.addEventListener("DOMContentLoaded", () => {
  const panel = document.getElementById("calendarEmbed");
  const trigger = document.getElementById("openCalendar");

  // ───────────────────────────────
  // JEŚLI NIE MA KALENDARZA NA STRONIE
  // ───────────────────────────────
  if (!panel || !trigger) {
    console.warn("⚠️ Panel kalendarza niedostępny na tej stronie.");
  } else {

    trigger.onclick = (e) => {
      e.stopPropagation();
      const isOpen = panel.style.display === "block";
      panel.style.display = isOpen ? "none" : "block";
    };

    // Kliknięcie poza panelem → zamknij
    document.addEventListener("click", (e) => {
      if (!panel.contains(e.target) && !trigger.contains(e.target)) {
        panel.style.display = "none";
      }
    });
  }

  /* ================================
   *  🎈 BOOTSTRAP TOOLTIP
   * ================================ */
  if (typeof bootstrap !== "undefined") {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].forEach((el) => {
      try {
        new bootstrap.Tooltip(el);
      } catch (err) {
        console.error("❌ Tooltip error:", err);
      }
    });
  } else {
    console.warn("⚠️ Bootstrap jeszcze nie załadowany — tooltips wyłączone.");
  }
});
