const express = require("express");
const router = express.Router();

const { listDays, loadDay } = require("../utils/json");

// REDIRECT → najnowszy plik
router.get("/", (req, res) => {
  const days = listDays();

  if (days.length === 0) {
    return res.render("zastepstwa", {
      title: "📅 Zastępstwa",
      active: "zastepstwa",
      dni: [],
      dzien: null,
      tryb: "class",
      zastepstwa: [],
      grouped: {},
      wolne: false
    });
  }

  const last = days[days.length - 1];
  res.redirect(`/zastepstwa/${last}`);
});

// WYŚWIETLANIE KONKRETNEGO DNIA
router.get("/:dzien", (req, res) => {
  const dni = listDays();
  const dzien = req.params.dzien;
  const tryb = req.query.tryb || "class";

  // brak pliku → redirect na najnowszy
  if (!dni.includes(dzien)) {
    const last = dni[dni.length - 1];
    return res.redirect(`/zastepstwa/${last}?tryb=${tryb}`);
  }

  const data = loadDay(dzien);
  if (!data) {
    const last = dni[dni.length - 1];
    return res.redirect(`/zastepstwa/${last}?tryb=${tryb}`);
  }

  // dzień wolny
  if (data.status === "wolne") {
    return res.render("zastepstwa", {
      title: `📅 Zastępstwa — ${dzien}`,
      active: "zastepstwa",
      dni,
      dzien,
      tryb,
      zastepstwa: [],
      grouped: {},
      wolne: true,
      opis: data.opis || "Dzień wolny"
    });
  }

  // normalne zastępstwa
  const zastepstwa = data;
  let grouped = {};

  if (tryb === "class") {
    for (const z of zastepstwa) {
      const key = z.klasa || "Nieznana klasa";
      (grouped[key] ??= []).push(z);
    }
  }

  if (tryb === "teacher") {
    for (const z of zastepstwa) {
      const key = z.nauczyciel_nieobecny || "Nieznany nauczyciel";
      (grouped[key] ??= []).push(z);
    }
  }

  res.render("zastepstwa", {
    title: `📅 Zastępstwa — ${dzien}`,
    active: "zastepstwa",
    dni,
    dzien,
    tryb,
    zastepstwa,
    grouped,
    wolne: false
  });
});

module.exports = router;
