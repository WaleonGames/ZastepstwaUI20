const express = require("express");
const router = express.Router();
const { ensureSettingsFile } = require("../middlewares/settings");
const fs = require("fs");
const path = require("path");

const SETTINGS_PATH = path.join(__dirname, "..", "config", "settings.json");

// ----------------------------------
// GET /ustawienia
// ----------------------------------
router.get("/", (req, res) => {
  const settings = ensureSettingsFile();

  res.render("ustawienia", {
    title: "⚙️ Ustawienia",
    active: "ustawienia",
    ...settings,           // ← theme, user, notifications, autoupdate, footer
    saved: false
  });
});

// ----------------------------------
// POST /ustawienia
// ----------------------------------
router.post("/", (req, res) => {
  const settings = ensureSettingsFile();

  // Motyw
  settings.theme = req.body.theme || "dark";

  // Język
  settings.user.lang = req.body.language || "pl";

  // System
  settings.notifications = req.body.notifications === "true";
  settings.autoupdate = req.body.autoupdate === "true";

  // FOOTER – NOWE USTAWIENIA
  settings.footer.mode = req.body.footerMode || "icons"; // icons | icons-text
  settings.footer.dateFormat = req.body.dateFormat || "horizontal"; // horizontal | vertical

  // Zapis do pliku
  fs.writeFileSync(SETTINGS_PATH, JSON.stringify(settings, null, 2));

  res.json({ success: true });
});

module.exports = router;
