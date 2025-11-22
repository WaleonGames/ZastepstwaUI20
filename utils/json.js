const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");
const ZAST_DIR = path.join(DATA_DIR, "zastepstwa");

// ===============================
// Uniwersalne wczytywanie JSON
// ===============================
function loadJSON(filePath) {
  try {
    const fullPath = path.join(DATA_DIR, filePath);
    return JSON.parse(fs.readFileSync(fullPath, "utf8"));
  } catch (err) {
    console.warn(`⚠️ Nie udało się wczytać JSON: ${filePath}:`, err.message);
    return {};
  }
}

// ===============================
// Lista dni zastępstw
// ===============================
function listDays() {
  if (!fs.existsSync(ZAST_DIR)) return [];

  return fs.readdirSync(ZAST_DIR)
    .filter(name => name.endsWith(".json"))
    .map(name => name.replace(".json", ""))
    .sort(); // chronologicznie
}

// ===============================
// Ładowanie pliku konkretnej daty
// ===============================
function loadDay(dateISO) {
  const file = path.join(ZAST_DIR, `${dateISO}.json`);
  if (!fs.existsSync(file)) return null;

  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return null;
  }
}

module.exports = {
  loadJSON,
  listDays,
  loadDay
};
