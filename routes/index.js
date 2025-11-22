const express = require("express");
const router = express.Router();
const { loadJSON } = require("../utils/json");

// Strona główna
router.get("/", (req, res) => {
  const nauczyciele = loadJSON("nauczyciele.json");

  const nieobecni = nauczyciele.filter(n => n.obecnosc === "no");
  const powody = {};

  nieobecni.forEach(n => {
    if (n.powod) powody[n.powod] = (powody[n.powod] || 0) + 1;
  });

  const dominujacyPowod =
    Object.keys(powody).length
      ? Object.entries(powody).sort((a, b) => b[1] - a[1])[0][0]
      : "Brak";

  res.render("index", {
    title: "Panel Publicznego Ucznia",
    active: "home",
    statystyka: {
      liczbaNieobecnych: nieobecni.length,
      dominujacyPowod
    },
    wydarzenia: [
      { data: "2025-11-10", tytul: "Akademia z okazji Święta Niepodległości" },
      { data: "2025-11-15", tytul: "Konkurs matematyczny" },
      { data: "2025-11-21", tytul: "Wywiadówki klas 3 i 4" },
      { data: "2025-11-25", tytul: "Dzień sportu szkolnego" }
    ]
  });
});

module.exports = router;
