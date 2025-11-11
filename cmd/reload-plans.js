const fs = require("fs");
const path = require("path");

exports.run = async () => {
  const dir = path.join(__dirname, "../plany");
  if (!fs.existsSync(dir)) return ["⚠️ Katalog 'plany/' nie istnieje."];

  const files = fs.readdirSync(dir).filter(f => f.endsWith(".json"));
  return [`🔄 Załadowano ponownie ${files.length} planów lekcji.`];
};
