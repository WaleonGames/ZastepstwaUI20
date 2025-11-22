const express = require("express");
const router = express.Router();
const path = require("path");

const { loadJSON } = require("../utils/json");

// Strona z listą klas
router.get("/", (req, res) => {
  const klasy = loadJSON("klasy.json");

  res.render("klasy", {
    title: "🏫 Klasy i uczniowie",
    active: "klasy",
    klasy
  });
});

// Plan klasy
router.get("/:nazwa", (req, res) => {
  const nazwa = req.params.nazwa.toUpperCase();
  const plan = loadJSON(path.join("plany", `${nazwa}.json`));
  const zastepstwaAll = loadJSON("zastepstwa.json");

  const wszystkie = Object.values(zastepstwaAll).flat();

  const zastepstwa = wszystkie.filter(z => {
    const K = (z.klasa || "").toUpperCase();
    const O = (z.opis || "").toUpperCase();
    return K === nazwa || O.includes(` ${nazwa}`) || O.includes(`${nazwa} `);
  });

  if (plan && Object.keys(plan).length) {
    for (const day of Object.keys(plan)) {
      for (const lekcja of plan[day]) {
        const match = zastepstwa.find(z =>
          (z.godzina || "").trim() === (lekcja.godzina || "").trim() &&
          (z.przedmiot || "").trim().toLowerCase() ===
          (lekcja.przedmiot || "").trim().toLowerCase()
        );

        if (match) {
          lekcja.zastepstwo = { ...match };
        }
      }
    }
  }

  res.render("plan", {
    title: `🗓 Plan lekcji — ${nazwa}`,
    active: "klasy",
    nazwa,
    plan: Object.keys(plan).length ? plan : null,
    zastepstwa
  });
});

module.exports = router;
