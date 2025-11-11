const os = require("os");
exports.run = async () => [
  "🧠 Terminal Zastępstwa",
  `💻 System: ${os.platform()} ${os.release()}`,
  `📁 Katalog: ${process.cwd()}`,
  `📅 Czas: ${new Date().toLocaleString("pl-PL")}`
];
