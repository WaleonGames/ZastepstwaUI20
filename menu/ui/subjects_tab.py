import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class SubjectsTab:
    def __init__(self, notebook, data_dir):
        self.data_dir = data_dir
        self.file = os.path.join(data_dir, "przedmioty.json")

        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Przedmioty")

        ttk.Label(frame, text="📚 Lista przedmiotów",
                  font=("Segoe UI", 14, "bold")).pack(pady=10)

        # ========================
        # TABELA
        # ========================
        cols = ("nazwa", "godziny", "klasy")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)

        self.tree.heading("nazwa", text="Przedmiot")
        self.tree.heading("godziny", text="Godziny / tydz.")
        self.tree.heading("klasy", text="Klasy")

        self.tree.column("nazwa", width=200)
        self.tree.column("godziny", width=120)
        self.tree.column("klasy", width=340)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ========================
        # PRZYCISKI
        # ========================
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Dodaj", command=self.add).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń", command=self.delete).pack(side="left", padx=5)

        self.load()

    # ========================
    # POBIERANIE WYBRANEGO
    # ========================
    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Nie wybrano przedmiotu.")
            return None

        values = self.tree.item(sel[0])["values"]

        return {
            "nazwa": values[0],
            "godziny": values[1],
            "klasy": values[2].split(", ") if values[2] else []
        }

    # ========================
    # ŁADOWANIE DANYCH
    # ========================
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        przedmioty = load_json(self.file)

        for nazwa, info in przedmioty.items():
            self.tree.insert("", "end", values=(
                nazwa,
                info.get("godziny", "?"),
                ", ".join(info.get("klasy", []))
            ))

    # ========================
    # DODAWANIE
    # ========================
    def add(self):
        AddEditSubject(self, mode="add")

    # ========================
    # EDYCJA
    # ========================
    def edit(self):
        subject = self.get_selected()
        if subject:
            AddEditSubject(self, mode="edit", subject=subject)

    # ========================
    # USUWANIE
    # ========================
    def delete(self):
        subject = self.get_selected()
        if not subject:
            return

        if not messagebox.askyesno("Usuń przedmiot", f"Czy chcesz usunąć przedmiot: {subject['nazwa']}?"):
            return

        przedmioty = load_json(self.file)
        przedmioty.pop(subject["nazwa"], None)

        save_json(self.file, przedmioty)
        self.load()


# =========================================================
# OKNO DODAWANIA / EDYCJI PRZEDMIOTU
# =========================================================

class AddEditSubject:
    def __init__(self, parent, mode, subject=None):
        self.parent = parent
        self.mode = mode
        self.subject = subject

        self.win = tk.Toplevel()
        self.win.title("Dodaj przedmiot" if mode == "add" else "Edytuj przedmiot")
        self.win.geometry("350x350")
        self.win.resizable(False, False)

        # ========================
        # POLA
        # ========================
        ttk.Label(self.win, text="Nazwa przedmiotu:").pack(pady=4)
        self.nazwa = ttk.Entry(self.win)
        self.nazwa.pack(fill="x", padx=10)

        ttk.Label(self.win, text="Liczba godzin tygodniowo:").pack(pady=4)
        self.godziny = ttk.Entry(self.win)
        self.godziny.pack(fill="x", padx=10)

        ttk.Label(self.win, text="Klasy (oddzielone przecinkami):").pack(pady=4)
        self.klasy = ttk.Entry(self.win)
        self.klasy.pack(fill="x", padx=10)

        ttk.Button(self.win, text="Zapisz", command=self.save).pack(pady=10)

        # Tryb edycji
        if mode == "edit" and subject:
            self.nazwa.insert(0, subject["nazwa"])
            self.godziny.insert(0, subject["godziny"])
            self.klasy.insert(0, ", ".join(subject["klasy"]))

    # ========================
    # ZAPIS
    # ========================
    def save(self):
        nazwa = self.nazwa.get().strip()
        godziny = int(self.godziny.get())
        klasy = [k.strip() for k in self.klasy.get().split(",") if k.strip()]

        if not nazwa:
            messagebox.showerror("Błąd", "Nazwa przedmiotu nie może być pusta.")
            return

        przedmioty = load_json(self.parent.file)

        data = {
            "godziny": godziny,
            "klasy": klasy,
            "etapy": [1, 2, 3]  # można zmienić/rozszerzyć
        }

        if self.mode == "add":
            przedmioty[nazwa] = data
        else:
            przedmioty[nazwa] = data

        save_json(self.parent.file, przedmioty)
        self.parent.load()
        self.win.destroy()
