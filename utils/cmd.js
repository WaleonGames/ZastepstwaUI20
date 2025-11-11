// utils/cmd.js
const fs = require("fs");
const path = require("path");

/**
 * Dynamiczny loader poleceń z katalogu /cmd/
 */
function loadCommands() {
  const cmdDir = path.join(__dirname, "../cmd");
  const commands = {};

  if (!fs.existsSync(cmdDir)) fs.mkdirSync(cmdDir, { recursive: true });

  fs.readdirSync(cmdDir)
    .filter(f => f.endsWith(".js"))
    .forEach(file => {
      const name = file.replace(".js", "").toLowerCase();
      try {
        const cmdModule = require(path.join(cmdDir, file));
        if (typeof cmdModule.run === "function") {
          commands[name] = cmdModule.run;
        }
      } catch (err) {
        console.error(`❌ Błąd ładowania komendy ${file}:`, err);
      }
    });

  return commands;
}

const commands = loadCommands();

/**
 * Uruchamia komendę terminala
 */
async function runCommand(input) {
  const cmd = input.trim().split(" ")[0].toLowerCase();
  const args = input.split(" ").slice(1);

  if (commands[cmd]) {
    try {
      const result = await commands[cmd](args);
      return {
        success: true,
        output: Array.isArray(result) ? result : [String(result)],
        type: "info"
      };
    } catch (err) {
      return { success: false, output: [err.message], type: "error" };
    }
  } else {
    return { success: false, output: [`❌ Nieznane polecenie: ${cmd}`], type: "error" };
  }
}

module.exports = { runCommand };
