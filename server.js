const express = require("express");
const crypto = require("crypto");
const cookieParser = require("cookie-parser")
const path = require("path");
const fs = require("fs");
const app = express();
const PORT = 3001;

const { runCommand } = require("./utils/cmd");

// === EJS SETUP ===
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public")));

app.use(express.json()); // ← obsługa JSON z fetch()
app.use(express.urlencoded({ extended: true })); // ← obsługa zwykłych formularzy POST

function generateAccessKey() {
  return crypto.randomBytes(75).toString("base64").slice(0, 100);
}

const SETTINGS_PATH = path.join(__dirname, "config", "settings.json");

// === UNIWERSALNE WCZYTYWANIE JSON ===
function loadJSON(filePath) {
  try {
    const fullPath = path.join(__dirname, 'data', filePath);
    const data = fs.readFileSync(fullPath, "utf8");
    return JSON.parse(data);
  } catch (err) {
    console.warn(`⚠️ Nie udało się wczytać pliku ${filePath}:`, err.message);
    return {};
  }
}

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
    console.log("🆕 Utworzono domyślny plik ustawień.");
    return defaults;
  }

  try {
    const data = JSON.parse(fs.readFileSync(SETTINGS_PATH, "utf8"));
    return {
      theme: data.theme || "dark",
      user: data.user || { lang: "pl" },
      notifications: data.notifications ?? false,
      autoupdate: data.autoupdate ?? false
    };
  } catch (err) {
    console.error("⚠️ Błąd w pliku ustawień, przywrócono domyślne:", err);
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
  console.log("💾 Zapisano ustawienia:", settings);
}

function requireTerminalAccess(req, res, next) {
  if (req.hasTerminalAccess) return next();

  return res.status(403).render("403", {
    title: "Brak dostępu",
    active: null,
    message: "🔒 Ten tryb jest dostępny tylko lokalnie przez skrót klawiaturowy."
  });
}

// === ROUTES ===

// === Globalny middleware: motyw aplikacji ===
app.use(cookieParser());

// === Globalny middleware: motyw + ukryty terminal ===
app.use((req, res, next) => {
  const settings = ensureSettingsFile();
  res.locals.theme = settings.theme;

  // --- Ustawienia dostępu do terminala ---
  const terminalPath = "/terminal";
  const adminPass = "SuperHaslo2025!"; // 🔐 Ustal swoje hasło administratora

  if (req.path === terminalPath) {
    const cookieKey = req.cookies.terminalKey;
    const queryKey = req.query.key;

    console.log("🧠 [TERMINAL CHECK]");
    console.log("• IP:", req.ip);
    console.log("• cookieKey:", cookieKey ? cookieKey.slice(0, 10) + "..." : "brak");
    console.log("• queryKey:", queryKey ? "***" : "brak");

    // === Warunek 1: poprawny cookie (100 znaków) ===
    if (cookieKey && cookieKey.length === 100) {
      console.log("✅ [TERMINAL ACCESS GRANTED via COOKIE]");
      return res.render("terminal", {
        title: "🧠 Terminal Zastępstw",
        theme: settings.theme,
      });
    }

    // === Warunek 2: wejście przez klucz administratora ===
    if (queryKey && queryKey === adminPass) {
      const newKey = crypto.randomBytes(75).toString("base64").slice(0, 100);
      res.cookie("terminalKey", newKey, {
        httpOnly: true,
        sameSite: "strict",
        maxAge: 60 * 60 * 1000, // 1h
      });
      console.log(`🔑 [TERMINAL ACCESS GRANTED via URL KEY] ${req.ip}`);
      console.log(`→ Utworzono sesyjny klucz: ${newKey.slice(0, 10)}...`);
      return res.render("terminal", {
        title: "🧠 Terminal Zastępstw",
        theme: settings.theme,
      });
    }

    // === Brak dostępu ===
    console.log("❌ [TERMINAL ACCESS DENIED]");
    return res.status(403).render("403", {
      title: "403 – Brak dostępu",
      active: null,
      message: "🔒 Dostęp tylko przez skrót (Windows + W) lub link z hasłem administratora.",
    });
  }

  next();
});

// === Strona główna ===
app.get("/", (req, res) => {
  const nauczyciele = loadJSON("nauczyciele.json");

  const nieobecni = nauczyciele.filter(n => n.obecnosc === "no");
  const powody = {};
  nieobecni.forEach(n => {
    if (n.powod) powody[n.powod] = (powody[n.powod] || 0) + 1;
  });

  const dominujacyPowod =
    Object.keys(powody).length > 0
      ? Object.entries(powody).sort((a, b) => b[1] - a[1])[0][0]
      : "Brak";

  const statystyka = {
    liczbaNieobecnych: nieobecni.length,
    dominujacyPowod
  };

  const wydarzenia = [
    { data: "2025-11-10", tytul: "Akademia z okazji Święta Niepodległości" },
    { data: "2025-11-15", tytul: "Konkurs matematyczny" },
    { data: "2025-11-21", tytul: "Wywiadówki klas 3 i 4" },
    { data: "2025-11-25", tytul: "Dzień sportu szkolnego" }
  ];

  res.render("index", {
    title: "Panel Publicznego Ucznia",
    active: "home",
    statystyka,
    wydarzenia
  });
});

// Domyślny widok (bez dnia)
app.get("/zastepstwa", (req, res) => {
  res.redirect("/zastepstwa/poniedzialek");
});

// Wg dnia
app.get("/zastepstwa/:dzien", (req, res) => {
  const plan = loadJSON("zastepstwa.json");
  const dni = Object.keys(plan || {});
  const dzien = req.params.dzien || "poniedzialek";
  const tryb = req.query.tryb || "class";

  let zastepstwa = plan[dzien] || [];

  let grouped = {};

  // Grupowanie + sortowanie wg trybu
  if (tryb === "class") {
    // Grupowanie po klasach
    zastepstwa.forEach(z => {
      const key = z.klasa || "Nieznana klasa";
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(z);
    });

    // === Sortowanie po klasie (1A → 1B → 2A → 2B ...) ===
    const collator = new Intl.Collator("pl", { numeric: true, sensitivity: "base" });
    grouped = Object.fromEntries(
      Object.entries(grouped).sort(([a], [b]) => collator.compare(a, b))
    );
  }

  else if (tryb === "teacher") {
    // Grupowanie po nieobecnym nauczycielu (A→Z)
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

// === Klasy ===
app.get("/klasy", (req, res) => {
  const klasy = loadJSON("klasy.json");

  res.render("klasy", {
    title: "🏫 Klasy i uczniowie",
    active: "klasy",
    klasy
  });
});

// === Plan lekcji dla klasy (z uwzględnieniem wszystkich zastępstw) ===
app.get("/klasy/:nazwa", (req, res) => {
  const nazwa = req.params.nazwa.toUpperCase(); // np. 1A
  const planPath = path.join("plany", `${nazwa}.json`);
  const plan = loadJSON(planPath);
  const zastepstwaAll = loadJSON("zastepstwa.json");

  // Połącz wszystkie dni z zastepstwa.json w jedną listę
  const wszystkieZastepstwa = Object.values(zastepstwaAll).flat();

  // Dopasuj tylko te, które dotyczą danej klasy (bezpośrednio lub w opisie)
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

  // Połącz plan z zastępstwami
  if (plan && Object.keys(plan).length) {
    Object.keys(plan).forEach(day => {
      plan[day].forEach(lekcja => {
        const match = zastepstwa.find(z =>
          z.godzina.trim() === lekcja.godzina.trim() &&
          z.przedmiot.trim().toLowerCase() === lekcja.przedmiot.trim().toLowerCase()
        );

        if (match) {
          lekcja.zastepstwo = {
            status: match.status,
            nauczyciel_nieobecny: match.nauczyciel_nieobecny,
            nauczyciel_zastepujacy: match.nauczyciel_zastepujacy,
            opis: match.opis
          };
        }
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

// === Nauczyciele ===
app.get("/nauczyciele", (req, res) => {
  const nauczyciele = loadJSON("nauczyciele.json");

  res.render("nauczyciele", {
    title: "👩‍🏫 Nauczyciele",
    active: "nauczyciele",
    nauczyciele
  });
});

// === Strona ustawień ===
app.get("/ustawienia", (req, res) => {
  const settings = ensureSettingsFile();

  res.render("ustawienia", {
    title: "⚙️ Ustawienia",
    active: "ustawienia",
    theme: settings.theme,
    user: settings.user,
    notifications: settings.notifications,
    autoupdate: settings.autoupdate,
    saved: false
  });
});

// === Zapis ustawień ===
app.post("/ustawienia", (req, res) => {
  const settings = ensureSettingsFile();

  // 🔹 Aktualizacja danych
  settings.theme = req.body.theme || "dark";
  settings.user.lang = req.body.language || "pl";
  settings.notifications = req.body.notifications === "true" || req.body.notifications === true;
  settings.autoupdate = req.body.autoupdate === "true" || req.body.autoupdate === true;

  // 🔹 Zapis pliku
  saveSettings(settings);

  res.json({ success: true });
});

// === Aktywacja terminala (skrót Win + W) ===
app.get("/activate-terminal", (req, res) => {
  const newKey = crypto.randomBytes(75).toString("base64").slice(0, 100);
  res.cookie("terminalKey", newKey, {
    httpOnly: true,
    sameSite: "strict",
    maxAge: 60 * 60 * 1000,
  });

  console.log(`🔑 [TERMINAL ENABLED] IP=${req.ip} | KEY=${newKey.slice(0, 10)}...`);
  res.redirect("/terminal");
});

// === Wylogowanie z terminala ===
app.get("/logout-terminal", (req, res) => {
  console.log(`👋 [TERMINAL] Wylogowano użytkownika IP=${req.ip}`);
  res.clearCookie("terminalKey", { httpOnly: true, sameSite: "strict" });
  res.redirect("/");
});

app.post("/api/terminal", async (req, res) => {
  const key = req.cookies.terminalKey;
  if (!key || key.length < 50)
    return res.status(403).json({ success: false, output: ["Brak dostępu do terminala."] });

  const cmd = req.body.command;
  if (!cmd) return res.json({ success: false, output: ["Brak polecenia."] });

  const result = await runCommand(cmd);
  res.json(result);
});

// === Fallback 404 ===
app.use((req, res) => {
  res.status(404).render("404", {
    title: "Nie znaleziono strony",
    active: null
  });
});

// === Start serwera ===
app.listen(PORT, () => {
  console.log(`🚀 Serwer działa pod adresem: http://localhost:${PORT}`);
});
