import os
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class ZastepstwaTab:
    def __init__(self, notebook, data_dir):
        # === USTALENIE KATALOGU GŁÓWNEGO PROJEKTU ===
        self.base_dir = os.path.abspath(os.path.join(data_dir, ".."))

        self.data_dir = os.path.join(self.base_dir, "data")
        self.file = os.path.join(self.data_dir, "zastepstwa.json")
        self.script = os.path.join(self.base_dir, "zastepstwa.py")

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
            text="🔄 Generuj zastępstwa",
            command=self.generate
        ).pack(side="left", padx=5)

        ttk.Button(
            top_buttons,
            text="🔁 Odśwież",
            command=self.refresh
        ).pack(side="left", padx=5)

        # ------------------------------------------------
        # TABELA ZESTAWIEŃ
        # ------------------------------------------------
        cols = ("dzien", "ilosc")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)

        self.tree.heading("dzien", text="Dzień")
        self.tree.heading("ilosc", text="Ilość zastępstw")

        self.tree.column("dzien", width=180)
        self.tree.column("ilosc", width=150)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Double-click → Otwórz szczegóły dnia
        self.tree.bind("<Double-1>", self.on_day_double_click)

        # ------------------------------------------------
        # LOG Z GENERATORA
        # ------------------------------------------------
        ttk.Label(frame, text="📄 Log generatora:", font=("Segoe UI", 11, "bold")).pack(pady=(5, 0))
        self.log = scrolledtext.ScrolledText(frame, height=10, font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

        self.load()

    # ------------------------------------------------
    # ŁADOWANIE
    # ------------------------------------------------
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            with open(self.file, "r", encoding="utf-8") as f:
                plan = json.load(f)
        except:
            return

        for dzien, lista in plan.items():
            self.tree.insert("", "end", values=(dzien, len(lista)))

    def refresh(self):
        self.load()
        messagebox.showinfo("Odświeżono", "Lista zastępstw została odświeżona.")

    # ------------------------------------------------
    # DOUBLE CLICK – SZCZEGÓŁY DNIA
    # ------------------------------------------------
    def on_day_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return

        dzien = self.tree.item(item)["values"][0]
        self.show_day_details(dzien)

    # ------------------------------------------------
    # OKNO SZCZEGÓŁÓW DNIA
    # ------------------------------------------------
    def show_day_details(self, dzien):
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                plan = json.load(f)
        except:
            messagebox.showerror("Błąd", "Nie można wczytać zastepstwa.json")
            return

        lista = plan.get(dzien, [])

        win = tk.Toplevel()
        win.title(f"Zastępstwa — {dzien}")
        win.geometry("620x480")

        ttk.Label(win, text=f"📅 Zastępstwa — {dzien}", font=("Segoe UI", 13, "bold")).pack(pady=10)

        cols = ("godzina", "klasa", "przedmiot", "status", "zastepujacy")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=18)

        tree.heading("godzina", text="Godzina")
        tree.heading("klasa", text="Klasa")
        tree.heading("przedmiot", text="Przedmiot")
        tree.heading("status", text="Status")
        tree.heading("zastepujacy", text="Zastępujący")

        tree.column("godzina", width=100)
        tree.column("klasa", width=80)
        tree.column("przedmiot", width=150)
        tree.column("status", width=120)
        tree.column("zastepujacy", width=150)

        tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Wstawianie danych
        for z in lista:
            tree.insert("", "end", values=(
                z.get("godzina"),
                z.get("klasa"),
                z.get("przedmiot"),
                z.get("status"),
                z.get("nauczyciel_zastepujacy") or "—"
            ))

        # double click → szczegóły pojedynczego wpisu
        tree.bind("<Double-1>", lambda e: self.show_entry_details(tree, lista))

    # ------------------------------------------------
    # SZCZEGÓŁY POJEDYNCZEGO ZASTĘPSTWA
    # ------------------------------------------------
    def show_entry_details(self, tree, lista):
        item = tree.selection()
        if not item:
            return

        index = tree.index(item)
        data = lista[index]

        win = tk.Toplevel()
        win.title("Szczegóły zastępstwa")
        win.geometry("420x400")

        ttk.Label(win, text="📘 Szczegóły zastępstwa", font=("Segoe UI", 12, "bold")).pack(pady=10)

        text = tk.Text(win, height=18, font=("Consolas", 10))
        text.pack(fill="both", expand=True, padx=10, pady=10)

        info = [
            f"Godzina: {data.get('godzina')}",
            f"Klasa: {data.get('klasa')}",
            f"Przedmiot: {data.get('przedmiot')}",
            f"Nauczyciel nieobecny: {data.get('nauczyciel_nieobecny')}",
            f"Nauczyciel zastępujący: {data.get('nauczyciel_zastepujacy') or '—'}",
            f"Status: {data.get('status')}",
            "",
            "Opis:",
            data.get("opis", "—")
        ]

        text.insert("end", "\n".join(info))
        text.config(state="disabled")

    # ------------------------------------------------
    # GENEROWANIE ZASTĘPSTW
    # ------------------------------------------------
    def generate(self):

        if not os.path.exists(self.script):
            messagebox.showerror("Błąd", f"Nie znaleziono pliku:\n{self.script}")
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
            messagebox.showerror("Błąd", f"Nie udało się wygenerować zastępstw:\n{e}")
            return

        self.load()
        messagebox.showinfo("Gotowe!", "Zastępstwa zostały wygenerowane.")
