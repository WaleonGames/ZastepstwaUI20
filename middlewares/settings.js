const fs = require("fs");
const path = require("path");

const SETTINGS_PATH = path.join(__dirname, "..", "config", "settings.json");

function ensureSettingsFile() {
  const defaults = {
    theme: "dark",
    user: { lang: "pl" },
    notifications: false,
    autoupdate: false,
    footer: {
      mode: "icons",
      dateFormat: "horizontal"
    }
  };

  if (!fs.existsSync(SETTINGS_PATH)) {
    fs.writeFileSync(SETTINGS_PATH, JSON.stringify(defaults, null, 2));
    return defaults;
  }

  try {
    const data = JSON.parse(fs.readFileSync(SETTINGS_PATH, "utf8"));

    // Auto-uzupełnienie brakujących pól
    data.footer = data.footer || defaults.footer;
    if (!data.footer.mode) data.footer.mode = "icons";
    if (!data.footer.dateFormat) data.footer.dateFormat = "horizontal";

    return data;
  } catch {
    fs.writeFileSync(SETTINGS_PATH, JSON.stringify(defaults, null, 2));
    return defaults;
  }
}

function settingsMiddleware(req, res, next) {
  const settings = ensureSettingsFile();

  res.locals.theme = settings.theme;
  res.locals.user = settings.user;
  res.locals.notifications = settings.notifications;
  res.locals.autoupdate = settings.autoupdate;
  res.locals.footerMode = settings.footer.mode;
  res.locals.dateFormat = settings.footer.dateFormat;
  res.locals.settings = settings;

  next();
}

module.exports = settingsMiddleware;
module.exports.ensureSettingsFile = ensureSettingsFile;
