# 🏫 ZastępstwaUI – System wyświetlania zastępstw szkolnych

**ZastępstwaUI** to lokalna aplikacja serwerowa (Node.js + EJS) służąca do zarządzania i prezentowania planów lekcji oraz zastępstw dla uczniów i nauczycieli.

---

## 🚀 Funkcje

- ✅ Przeglądanie planów lekcji (`/plan`)
- 👨‍🏫 Widok nauczycieli (`/nauczyciele`)
- 🧑‍🎓 Widok klas (`/klasy`)
- 🔁 Zastępstwa (`/zastepstwa`)
- 🧩 Terminal komend administracyjnych (katalog `cmd/`)
- ⚙️ Moduł ustawień (`/ustawienia`)
- 🧠 Wsparcie dla integracji z Python (np. `plans.py`, `zastepstwa.py`)

---

## 🧩 Struktura katalogów

```
project-root/
├── cmd/ # Komendy serwera (np. info, reload, show-logs)
├── config/ # Pliki konfiguracyjne (np. API, ścieżki)
├── data/ # Dane robocze (np. JSON z planami i zastępstwami)
├── public/ # Zasoby statyczne (CSS, JS, obrazy)
├── utils/ # Narzędzia (np. parser komend)
├── views/ # Widoki EJS
│ ├── partials/ # Fragmenty (nagłówki, 404)
│ ├── index.ejs # Strona główna
│ ├── plan.ejs # Plan lekcji
│ ├── zastepstwa.ejs # Zastępstwa
│ └── terminal.ejs # Terminal administracyjny
├── plans.py # Skrypt Python do generowania planów
├── zastepstwa.py # Skrypt Python do pobierania zastępstw
├── server.js # Główny serwer Express
├── package.json # Konfiguracja npm
└── README.md
```

---

## ⚙️ Instalacja i uruchomienie

### 1️⃣ Zainstaluj zależności
```bash
npm install
```

### 2️⃣ Uruchom serwer
```bash
node server.js
```

---

## 🧑‍💻 Terminal komend (cmd/)

Możesz uruchamiać wewnętrzne komendy np.:

```
node utils/cmd.js info
node utils/cmd.js reload-plans
node utils/cmd.js zastepstwa
```

## 🧰 Wymagania systemowe

- Node.js 18+
- Python 3.10+
- Przeglądarka wspierająca HTML5 / EJS (Chrome, Firefox, Edge)

## 📄 Licencja

Projekt edukacyjny – © 2025 HTGMC / Kacper Programuje

Nie przeznaczony do użytku komercyjnego tylko szkolnej.


---

## ⚫ **.gitignore (zalecany dla projektu Node.js + Python)**

```gitignore
# === Node.js ===
node_modules/
npm-debug.log*
package-lock.json

# === Python ===
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/
.env

# === Systemowe ===
.DS_Store
Thumbs.db

# === Logi i dane ===
logs/
*.log
data/
config/*.json

# === IDE / edytory ===
.vscode/
.idea/
*.swp

# === Inne ===
state.json