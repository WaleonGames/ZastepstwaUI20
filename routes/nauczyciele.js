const express = require("express");
const router = express.Router();

const { loadJSON } = require("../utils/json");

router.get("/", (req, res) => {
  const nauczyciele = loadJSON("nauczyciele.json");

  res.render("nauczyciele", {
    title: "👩‍🏫 Nauczyciele",
    active: "nauczyciele",
    nauczyciele
  });
});

module.exports = router;
