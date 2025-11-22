require("dotenv").config();
const express = require("express");
const cookieParser = require("cookie-parser");
const path = require("path");
const app = express();
const PORT = 3001;

// === Middlewares ===
const uuidMiddleware = require("./middlewares/uuid");
const settingsMiddleware = require("./middlewares/settings");
const calendarMiddleware = require("./middlewares/calendar");

// === ROUTES ===
const indexRoute = require("./routes/index");
const zastRoute = require("./routes/zastepstwa");
const klasyRoute = require("./routes/klasy");
const naucRoute = require("./routes/nauczyciele");
const ustawieniaRoute = require("./routes/ustawienia");

// === CONFIG ===
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public")));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// === GLOBAL MIDDLEWARES ===
app.use(uuidMiddleware);
app.use(settingsMiddleware);
app.use(calendarMiddleware);

// === ROUTES ===
app.use("/", indexRoute);
app.use("/zastepstwa", zastRoute);
app.use("/klasy", klasyRoute);
app.use("/nauczyciele", naucRoute);
app.use("/ustawienia", ustawieniaRoute);

// === 404 ===
app.use((req, res) => {
  res.status(404).render("404", {
    title: "Nie znaleziono strony",
    active: null
  });
});

// === GLOBAL ERROR HANDLER ===
const { sendErrorToDiscord } = require("./utils/discord");

app.use(async (err, req, res, next) => {
  console.error("❌ Błąd aplikacji:", err);

  await sendErrorToDiscord(err.stack || err.message, req);

  res.status(500).render("500", {
    title: "Błąd serwera",
    active: null,
    errorId: Math.random().toString(36).slice(2, 10),
    error500: true
  });
});

// === START ===
app.listen(PORT, () =>
  console.log(`🚀 Serwer działa na http://localhost:${PORT}`)
);
