const fs = require("fs");
const path = require("path");

const CALENDAR_PATH = path.join(__dirname, "..", "data", "calendar.json");

// ===============================
// Ładowanie calendar.json
// ===============================
function loadCalendar() {
  try {
    return JSON.parse(fs.readFileSync(CALENDAR_PATH, "utf8"));
  } catch {
    return { title: "", opis: "", swieta: {} };
  }
}

// ===============================
// Czy dzień jest wolny?
// ===============================
function isFreeDay(iso, calendar) {
  if (!calendar || !calendar.swieta) return { free: false };

  for (const [name, val] of Object.entries(calendar.swieta)) {

    if (typeof val === "string" && val === iso)
      return { free: true, name };

    if (Array.isArray(val) && val.length === 2) {
      if (iso >= val[0] && iso <= val[1])
        return { free: true, name };
    }
  }

  return { free: false };
}

module.exports = { loadCalendar, isFreeDay };
