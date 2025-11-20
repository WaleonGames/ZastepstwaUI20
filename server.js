require("dotenv").config();
const express = require("express");
const crypto = require("crypto");
const cookieParser = require("cookie-parser");
// --- Fetch dla Node.js ---
const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));
const path = require("path");
const fs = require("fs");
const app = express();
const PORT = 3001;

const { runCommand } = require("./utils/cmd");

// === EJS SETUP ===
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public")));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser()); // cookie parser jako pierwszy middleware

function generateAccessKey() {
  return crypto.randomBytes(75).toString("base64").slice(0, 100);
}

const SETTINGS_PATH = path.join(__dirname, "config", "settings.json");

// === UNIWERSALNE WCZYTYWANIE JSON ===
function loadJSON(filePath) {
  try {
    const fullPath = path.join(__dirname, "data", filePath);
    return JSON.parse(fs.readFileSync(fullPath, "utf8"));
  } catch (err) {
    console.warn(`⚠️ Nie udało się wczytać pliku ${filePath}:`, err.message);
    return {};
  }
}

// === SETTINGS FILE MANAGEMENT ===
function ensureSettingsFile() {
  if (!fs.existsSync(SETTINGS_PATH)) {
    const defaults = {
      theme: "dark",
      user: { lang: "pl" },
      notifications: false,
      autoupdate: false
    };
    fs.mkdirSync(path.dirname(SETTINGS_PATH), { recursive: true });
    fs.writeFileSync(SETTINGS_PATH, JSON.stringify(defaults, null, 2));
    return defaults;
  }

  try {
    return JSON.parse(fs.readFileSync(SETTINGS_PATH, "utf8"));
  } catch (err) {
    const defaults = {
      theme: "dark",
      user: { lang: "pl" },
      notifications: false,
      autoupdate: false
    };
    fs.writeFileSync(SETTINGS_PATH, JSON.stringify(defaults, null, 2));
    return defaults;
  }
}

function saveSettings(settings) {
  fs.writeFileSync(SETTINGS_PATH, JSON.stringify(settings, null, 2));
}

async function sendErrorToDiscord(errorMessage, req) {
  try {
    const webhook = process.env.DISCORD_WEBHOOK;
    if (!webhook) {
      console.warn("⚠️ Brak DISCORD_WEBHOOK w .env");
      return;
    }

    const payload = {
      content: "🚨 **ZastepstwaUI21 – wykryto błąd 500!**",
      embeds: [
        {
          title: "Błąd 500 – szczegóły",
          color: 15158332,
          description: "Wystąpił krytyczny błąd aplikacji backend."
        },
        {
          title: "📌 Informacje o żądaniu",
          color: 3447003,
          fields: [
            { name: "Route", value: "`" + req.originalUrl + "`" },
            { name: "Metoda", value: "`" + req.method + "`" },
            { name: "IP", value: "`" + req.ip + "`" },
            { name: "User-Agent", value: "```" + (req.headers["user-agent"] || "brak") + "```" },
            { name: "UUID", value: "`" + (req.cookies.school_uuid || "brak") + "`" }
          ]
        },
        {
          title: "🛑 Log błędu",
          color: 15158332,
          description: "```\n" + (errorMessage || "brak danych") + "\n```"
        }
      ]
    };

    const response = await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      console.error("❌ Discord webhook error:", await response.text());
    } else {
      console.log("📤 Błąd wysłany na Discord!");
    }

  } catch (err) {
    console.error("❌ Nie udało się wysłać raportu na Discord:", err);
  }
}

// =======================================================
// ⭐ GLOBALNY MIDDLEWARE: school_uuid + motyw + kalendarz
// =======================================================
app.use((req, res, next) => {
  // --- SCHOOL UUID ---
  let uuid = req.cookies.school_uuid;

  if (!uuid) {
    uuid = crypto.randomUUID();
    res.cookie("school_uuid", uuid, {
      httpOnly: true,
      sameSite: "strict",
      secure: false,
      maxAge: 365 * 24 * 60 * 60 * 1000
    });
    console.log("🆕 Utworzono school_uuid:", uuid);
  } else {
    console.log("🍪 Istniejący school_uuid:", uuid);
  }

  res.locals.school_uuid = uuid;

  // --- SETTINGS ---
  const settings = ensureSettingsFile();
  res.locals.theme = settings.theme;

  // --- KALENDARZ ---
  const now = new Date();
  res.locals.calendar = {
    now,
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
    ],
  };

  next();
});

// =======================================================
// ROUTES
// =======================================================

// Strona główna
app.get("/", (req, res) => {
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

// Domyślne redirect → poniedziałek
app.get("/zastepstwa", (req, res) => {
  res.redirect("/zastepstwa/poniedzialek");
});

// Zastępstwa wg dnia
app.get("/zastepstwa/:dzien", (req, res) => {
  const plan = loadJSON("zastepstwa.json");
  const dzien = req.params.dzien;
  const tryb = req.query.tryb || "class";

  const dni = Object.keys(plan || {});
  let zastepstwa = plan[dzien] || [];

  let grouped = {};

  if (tryb === "class") {
    zastepstwa.forEach(z => {
      const key = z.klasa || "Nieznana klasa";
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(z);
    });

    const collator = new Intl.Collator("pl", { numeric: true, sensitivity: "base" });

    grouped = Object.fromEntries(
      Object.entries(grouped).sort(([a], [b]) => collator.compare(a, b))
    );
  }

  if (tryb === "teacher") {
    zastepstwa.forEach(z => {
      const key = z.nauczyciel_nieobecny || "Nieznany nauczyciel";
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(z);
    });

    grouped = Object.fromEntries(
      Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b, "pl"))
    );
  }

  res.render("zastepstwa", {
    title: "📅 Zastępstwa",
    active: "zastepstwa",
    dni,
    dzien,
    tryb,
    zastepstwa,
    grouped
  });
});

// Klasy
app.get("/klasy", (req, res) => {
  const klasy = loadJSON("klasy.json");
  res.render("klasy", {
    title: "🏫 Klasy i uczniowie",
    active: "klasy",
    klasy
  });
});

// Plan klasy
app.get("/klasy/:nazwa", (req, res) => {
  const nazwa = req.params.nazwa.toUpperCase();
  const plan = loadJSON(path.join("plany", `${nazwa}.json`));
  const zastepstwaAll = loadJSON("zastepstwa.json");
  const wszystkieZastepstwa = Object.values(zastepstwaAll).flat();

  const zastepstwa = wszystkieZastepstwa.filter(z => {
    const klasaZ = (z.klasa || "").toUpperCase();
    const opisZ = (z.opis || "").toUpperCase();
    return (
      klasaZ === nazwa ||
      opisZ.includes(` ${nazwa}`) ||
      opisZ.includes(`KLASY ${nazwa}`) ||
      opisZ.includes(`${nazwa} `)
    );
  });

  if (plan && Object.keys(plan).length) {
    Object.keys(plan).forEach(day => {
      plan[day].forEach(lekcja => {
        const match = zastepstwa.find(z =>
          (z.godzina || "").trim() === (lekcja.godzina || "").trim() &&
          (z.przedmiot || "").trim().toLowerCase() === (lekcja.przedmiot || "").trim().toLowerCase()
        );

        if (match)
          lekcja.zastepstwo = { ...match };
      });
    });
  }

  res.render("plan", {
    title: `🗓 Plan lekcji — ${nazwa}`,
    active: "plans",
    nazwa,
    plan: Object.keys(plan).length ? plan : null,
    zastepstwa
  });
});

// Nauczyciele
app.get("/nauczyciele", (req, res) => {
  const nauczyciele = loadJSON("nauczyciele.json");
  res.render("nauczyciele", {
    title: "👩‍🏫 Nauczyciele",
    active: "nauczyciele",
    nauczyciele
  });
});

// Ustawienia
app.get("/ustawienia", (req, res) => {
  const settings = ensureSettingsFile();

  res.render("ustawienia", {
    title: "⚙️ Ustawienia",
    active: "ustawienia",
    ...settings,
    saved: false
  });
});

// Zapis ustawień
app.post("/ustawienia", (req, res) => {
  const settings = ensureSettingsFile();

  settings.theme = req.body.theme || "dark";
  settings.user.lang = req.body.language || "pl";
  settings.notifications = req.body.notifications === "true";
  settings.autoupdate = req.body.autoupdate === "true";

  saveSettings(settings);
  res.json({ success: true });
});

// Fallback 404
app.use((req, res) => {
  res.status(404).render("404", {
    title: "Nie znaleziono strony",
    active: null
  });
});

// =======================================================
// 🛑 GLOBAL ERROR HANDLER (Błąd 500)
// =======================================================
app.use(async (err, req, res, next) => {
  console.error("❌ Błąd aplikacji:", err);

  // wysyłamy na Discord
  await sendErrorToDiscord(err.stack || err.message, req);

  res.status(500).render("500", {
    title: "Błąd serwera",
    active: null,
    errorId: crypto.randomBytes(6).toString("hex"),
    error500: true  // 🔥 nowa flaga wyłączająca header/footer
  });
});

// Start serwera
app.listen(PORT, () => {
  console.log(`🚀 Serwer działa: http://localhost:${PORT}`);
});
