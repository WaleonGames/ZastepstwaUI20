const fs = require("fs");
const path = require("path");

exports.run = async () => {
  const logPath = path.join(__dirname, "../logs/system.log");
  if (!fs.existsSync(logPath)) return ["⚠️ Brak pliku logów."];

  const lines = fs.readFileSync(logPath, "utf-8").trim().split("\n");
  return lines.slice(-15);
};
