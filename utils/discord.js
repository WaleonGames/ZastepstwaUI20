const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));

async function sendErrorToDiscord(errorMessage, req) {
  try {
    const webhook = process.env.DISCORD_WEBHOOK;
    if (!webhook) return;

    const payload = {
      embeds: [
        {
          title: "Błąd 500 — Informacje o zapytaniu",
          color: 15158332,
          fields: [
            { name: "Route", value: "`" + req.originalUrl + "`" },
            { name: "Metoda", value: "`" + req.method + "`" },
            { name: "IP", value: "`" + req.ip + "`" },
            {
              name: "User-Agent",
              value: "```" + (req.headers["user-agent"] || "brak") + "```"
            },
            {
              name: "UUID",
              value: "`" + (req.cookies.school_uuid || "brak") + "`"
            }
          ]
        },
        {
          title: "Stacktrace",
          color: 15158332,
          description: "```\n" + (errorMessage || "brak danych") + "\n```"
        }
      ]
    };

    await fetch(webhook, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (err) {
    console.error("❌ Nie udało wysłać błędu na Discord:", err);
  }
}

module.exports = { sendErrorToDiscord };
