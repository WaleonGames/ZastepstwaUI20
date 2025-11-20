/* ================================
 *  ⏰ ZEGAR
 * ================================ */
function updateClock() {
  const now = new Date();
  const h = now.getHours().toString().padStart(2, "0");
  const m = now.getMinutes().toString().padStart(2, "0");

  const d = now.getDate().toString().padStart(2, "0");
  const mo = (now.getMonth() + 1).toString().padStart(2, "0");
  const y = now.getFullYear();

  document.getElementById("footer-time").textContent = `${h}:${m}`;
  document.getElementById("footer-date").textContent = `${d}.${mo}.${y}`;
}

setInterval(updateClock, 1000);
updateClock();



/* ================================
 *  📂 OTWIERANIE/ZAMYKANIE PANELU
 * ================================ */
document.addEventListener("DOMContentLoaded", () => {
  const panel = document.getElementById("calendarEmbed");
  const trigger = document.getElementById("openCalendar");

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
});
