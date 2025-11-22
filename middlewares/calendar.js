const fs = require("fs");
const path = require("path");

const CALENDAR_PATH = path.join(__dirname, "..", "data", "calendar.json");

function loadCalendar() {
  try {
    return JSON.parse(fs.readFileSync(CALENDAR_PATH, "utf8"));
  } catch {
    return null;
  }
}

function calendarMiddleware(req, res, next) {
  const now = new Date();
  const iso = now.toISOString().slice(0, 10);

  const calendar = loadCalendar();
  let isFreeToday = false;
  let freeTodayName = null;

  // sprawdzamy dni wolne
  if (calendar?.swieta) {
    for (const [name, val] of Object.entries(calendar.swieta)) {
      if (typeof val === "string" && val === iso) {
        isFreeToday = true;
        freeTodayName = name;
      }

      if (Array.isArray(val)) {
        if (iso >= val[0] && iso <= val[1]) {
          isFreeToday = true;
          freeTodayName = name;
        }
      }
    }
  }

  res.locals.calendar = {
    now,
    iso,
    year: now.getFullYear(),
    month: now.getMonth(),
    day: now.getDate(),
    weekday: now.getDay(),
    monthsPL: [
      "Styczeń","Luty","Marzec","Kwiecień","Maj","Czerwiec",
      "Lipiec","Sierpień","Wrzesień","Październik","Listopad","Grudzień"
    ],
    daysPL: [
      "Niedziela","Poniedziałek","Wtorek","Środa",
      "Czwartek","Piątek","Sobota"
    ]
  };

  res.locals.schoolCalendar = calendar;
  res.locals.isFreeToday = isFreeToday;
  res.locals.freeTodayName = freeTodayName;

  next();
}

module.exports = calendarMiddleware;
