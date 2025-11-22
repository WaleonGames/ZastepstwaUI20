import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, date, timedelta


class ZastepstwaTab:
    def __init__(self, notebook, data_dir):

        # Katalog główny projektu
        self.base_dir = os.path.abspath(os.path.join(data_dir, ".."))

        self.data_dir = os.path.join(self.base_dir, "data")
        self.zastepstwa_dir = os.path.join(self.data_dir, "zastepstwa")
        self.script = os.path.join(self.base_dir, "zastepstwa.py")

        os.makedirs(self.zastepstwa_dir, exist_ok=True)

        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Zastępstwa")

        ttk.Label(frame, text="📅 Zastępstwa",
                  font=("Segoe UI", 14, "bold")).pack(pady=10)

        # ------------------------------------------------
        # PRZYCISKI
        # ------------------------------------------------
        top_buttons = ttk.Frame(frame)
        top_buttons.pack(fill="x", padx=10)

        ttk.Button(
            top_buttons,
            text="🔄 Generuj zastępstwa na jutro",
            command=self.generate
        ).pack(side="left", padx=5)

        ttk.Button(
            top_buttons,
            text="🔁 Odśwież",
            command=self.refresh
        ).pack(side="left", padx=5)

        # ------------------------------------------------
        # TABELA Z DNIAMI
        # ------------------------------------------------
        cols = ("dzien", "ilosc")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)

        self.tree.heading("dzien", text="Dzień")
        self.tree.heading("ilosc", text="Ilość zastępstw / Wolne")

        self.tree.column("dzien", width=200)
        self.tree.column("ilosc", width=180)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.bind("<Double-1>", self.on_day_double_click)

        # ------------------------------------------------
        # LOG
        # ------------------------------------------------
        ttk.Label(frame, text="📄 Log generatora:",
                  font=("Segoe UI", 11, "bold")).pack(pady=(5, 0))

        self.log = scrolledtext.ScrolledText(frame, height=10, font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

        self.load()

    # ============================================================
    # ODCZYT KALENDARZA
    # ============================================================
    def load_calendar(self):
        path = os.path.join(self.data_dir, "calendar.json")
        if not os.path.exists(path):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None

    # ============================================================
    # SPRAWDZENIE, CZY DZIEŃ JEST WOLNY
    # ============================================================
    def is_day_free(self, date_str):
        """Zwraca False jeśli dzień szkolny,
           lub dict jeśli dzień wolny."""

        calendar = self.load_calendar()
        if not calendar:
            return False

        d = datetime.strptime(date_str, "%Y-%m-%d").date()

        # WEEKEND
        if d.weekday() >= 5:
            return {"powod": "Weekend"}

        swieta = calendar.get("swieta", {})

        for nazwa, wartosc in swieta.items():

            # Jednodniowe
            if isinstance(wartosc, str):
                if wartosc == date_str:
                    return {"powod": nazwa}

            # Wielodniowe
            elif isinstance(wartosc, list) and len(wartosc) == 2:
                start = datetime.strptime(wartosc[0], "%Y-%m-%d").date()
                end = datetime.strptime(wartosc[1], "%Y-%m-%d").date()

                if start <= d <= end:
                    return {"powod": nazwa, "od": wartosc[0], "do": wartosc[1]}

        return False

    # ============================================================
    # ŁADOWANIE LISTY PLIKÓW
    # ============================================================
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        files = [f for f in os.listdir(self.zastepstwa_dir) if f.endswith(".json")]
        files.sort()

        for fname in files:
            path = os.path.join(self.zastepstwa_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, dict) and data.get("status") == "wolne":
                    ilosc = f"— (wolne: {data.get('powod')})"
                else:
                    ilosc = len(data)

                dzien = fname.replace(".json", "")

                self.tree.insert("", "end", values=(dzien, ilosc))

            except:
                continue

    def refresh(self):
        self.load()
        messagebox.showinfo("Odświeżono", "Lista została odświeżona.")

    # ============================================================
    # DOUBLE CLICK NA DZIEŃ
    # ============================================================
    def on_day_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return

        dzien = self.tree.item(item)["values"][0]
        self.show_day_details(dzien)

    # ============================================================
    # OKNO DETALE DNIA
    # ============================================================
    def show_day_details(self, dzien):
        path = os.path.join(self.zastepstwa_dir, f"{dzien}.json")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            messagebox.showerror("Błąd", f"Nie można otworzyć:\n{path}")
            return

        win = tk.Toplevel()
        win.title(f"Zastępstwa — {dzien}")
        win.geometry("660x540")

        ttk.Label(win, text=f"📅 Zastępstwa — {dzien}",
                  font=("Segoe UI", 13, "bold")).pack(pady=10)

        # Dzień wolny
        if isinstance(data, dict) and data.get("status") == "wolne":
            ttk.Label(win, text=f"🎉 Dzień wolny — {data.get('powod')}",
                      font=("Segoe UI", 12)).pack(pady=30)
            return

        cols = ("godzina", "klasa", "przedmiot", "status", "zastepujacy")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=18)

        for c in cols:
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=120)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for z in data:
            tree.insert("", "end", values=(
                z.get("godzina"),
                z.get("klasa"),
                z.get("przedmiot"),
                z.get("status"),
                z.get("nauczyciel_zastepujacy") or "—"
            ))

    # ============================================================
    # GENEROWANIE ZASTĘPSTW
    # ============================================================
    def generate(self):

        jutro = date.today() + timedelta(days=1)
        jutro_str = jutro.strftime("%Y-%m-%d")

        free = self.is_day_free(jutro_str)

        # Jeśli wolne — zapisujemy plik i kończymy
        if free:
            out_path = os.path.join(self.zastepstwa_dir, f"{jutro_str}.json")

            data = {
                "status": "wolne",
                "powod": free.get("powod"),
            }

            if "od" in free and "do" in free:
                data["od"] = free["od"]
                data["do"] = free["do"]

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.load()
            self.log.delete(1.0, "end")
            self.log.insert("end", f"{jutro_str} — dzień wolny.\nPowód: {free['powod']}")
            messagebox.showinfo("Dzień wolny", f"{jutro_str} — {free['powod']}")
            return

        # Normalne generowanie
        if not os.path.exists(self.script):
            messagebox.showerror("Błąd", f"Brak pliku:\n{self.script}")
            return

        try:
            result = subprocess.run(
                ["python3", self.script],
                cwd=self.base_dir,
                capture_output=True,
                text=True
            )

            self.log.delete(1.0, "end")
            self.log.insert("end", result.stdout)

            if result.stderr:
                self.log.insert("end", "\n[BŁĄD]\n" + result.stderr)

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wygenerować:\n{e}")
            return

        self.load()
        messagebox.showinfo("Gotowe!", "Zastępstwa wygenerowane.")
