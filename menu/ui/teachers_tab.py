import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class TeachersTab:
    def __init__(self, notebook, data_dir):
        self.data_dir = data_dir
        self.file = os.path.join(data_dir, "nauczyciele.json")

        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Nauczyciele")

        ttk.Label(self.frame, text="👩‍🏫 Lista nauczycieli",
                  font=("Segoe UI", 14, "bold")).pack(pady=10)

        # ============================
        # KOLUMNY TABELI
        # ============================
        cols = ("imie", "przedmiot", "sala", "etap", "obecnosc", "powod", "wychowawca")

        self.tree = ttk.Treeview(self.frame, columns=cols, show="headings", height=18)
        self.tree.pack(fill="both", expand=True, padx=10)

        headers = {
            "imie": "Imię",
            "przedmiot": "Przedmiot",
            "sala": "Sala",
            "etap": "Etap",
            "obecnosc": "Obecność",
            "powod": "Powód",
            "wychowawca": "Wychowawca?"
        }

        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=140)

        # ============================
        # Przyciski
        # ============================
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Dodaj", command=self.add).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń", command=self.delete).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Zmień status", command=self.toggle_status).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Powód nieobecności", command=self.set_reason).pack(side="left", padx=5)

        self.load()

    # ==================================================
    # Odczyt zaznaczonego nauczyciela
    # ==================================================
    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Nie wybrano nauczyciela.")
            return None

        values = self.tree.item(sel[0])["values"]

        return {
            "imie": values[0],
            "przedmiot": values[1],
            "sala": values[2],
            "etap": values[3],
            "obecnosc": "yes" if values[4] == "Obecny" else "no",
            "powod": values[5],
            "moze_byc_wychowawca": True if values[6] == "TAK" else False
        }

    # ==================================================
    # ŁADOWANIE TABELI
    # ==================================================
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        nauczyciele = load_json(self.file)

        for n in nauczyciele:
            self.tree.insert("", "end", values=(
                n.get("imie"),
                n.get("przedmiot"),
                n.get("sala"),
                n.get("etap"),
                "Obecny" if n.get("obecnosc") == "yes" else "Nieobecny",
                n.get("powod", "") if n.get("obecnosc") == "no" else "",
                "TAK" if n.get("moze_byc_wychowawca") else "NIE"
            ))

    # ==================================================
    # Dodawanie nauczyciela
    # ==================================================
    def add(self):
        AddEditTeacher(self, mode="add")

    # ==================================================
    # Edycja nauczyciela
    # ==================================================
    def edit(self):
        teacher = self.get_selected()
        if teacher:
            AddEditTeacher(self, mode="edit", teacher=teacher)

    # ==================================================
    # Usuwanie nauczyciela
    # ==================================================
    def delete(self):
        teacher = self.get_selected()
        if not teacher:
            return

        if not messagebox.askyesno("Usuń nauczyciela", f"Czy chcesz usunąć: {teacher['imie']}?"):
            return

        nauczyciele = load_json(self.file)
        nauczyciele = [n for n in nauczyciele if n["imie"] != teacher["imie"]]

        save_json(self.file, nauczyciele)
        self.load()

    # ==================================================
    # ZMIANA STATUSU OBECNOŚCI
    # ==================================================
    def toggle_status(self):
        teacher = self.get_selected()
        if not teacher:
            return

        nauczyciele = load_json(self.file)

        for n in nauczyciele:
            if n["imie"] == teacher["imie"]:

                if n["obecnosc"] == "yes":
                    n["obecnosc"] = "no"
                    n["powod"] = "Brak powodu"
                else:
                    n["obecnosc"] = "yes"
                    n.pop("powod", None)

                break

        save_json(self.file, nauczyciele)
        self.load()

    # ==================================================
    # Ustawienie powodu nieobecności
    # ==================================================
    def set_reason(self):
        teacher = self.get_selected()
        if not teacher:
            return

        if teacher["obecnosc"] == "yes":
            messagebox.showinfo("Informacja", "Nauczyciel jest obecny — brak powodu.")
            return

        reason = simpledialog.askstring("Powód nieobecności", "Podaj powód nieobecności:")
        if not reason:
            return

        nauczyciele = load_json(self.file)
        for n in nauczyciele:
            if n["imie"] == teacher["imie"]:
                n["powod"] = reason
                break

        save_json(self.file, nauczyciele)
        self.load()


# ==================================================
# OKNO Dodawania / Edycji nauczyciela
# ==================================================

class AddEditTeacher:
    def __init__(self, parent, mode, teacher=None):
        self.parent = parent
        self.mode = mode
        self.teacher = teacher

        self.win = tk.Toplevel()
        self.win.title("Dodaj nauczyciela" if mode == "add" else "Edytuj nauczyciela")
        self.win.geometry("350x380")
        self.win.resizable(False, False)

        # polA
        ttk.Label(self.win, text="Imię:").pack()
        self.imie = ttk.Entry(self.win)
        self.imie.pack(fill="x", padx=10, pady=4)

        ttk.Label(self.win, text="Przedmiot:").pack()
        self.przedmiot = ttk.Entry(self.win)
        self.przedmiot.pack(fill="x", padx=10, pady=4)

        ttk.Label(self.win, text="Sala:").pack()
        self.sala = ttk.Entry(self.win)
        self.sala.pack(fill="x", padx=10, pady=4)

        ttk.Label(self.win, text="Etap:").pack()
        self.etap = ttk.Entry(self.win)
        self.etap.pack(fill="x", padx=10, pady=4)

        self.wychowawca_var = tk.BooleanVar()
        ttk.Checkbutton(self.win, text="Może być wychowawcą", variable=self.wychowawca_var).pack(pady=6)

        ttk.Button(self.win,
                   text="Zapisz",
                   command=self.save
                   ).pack(pady=10)

        # Tryb edycji
        if mode == "edit" and teacher:
            self.imie.insert(0, teacher["imie"])
            self.przedmiot.insert(0, teacher["przedmiot"])
            self.sala.insert(0, teacher["sala"])
            self.etap.insert(0, teacher["etap"])
            self.wychowawca_var.set(teacher["moze_byc_wychowawca"])

    def save(self):
        nauczyciele = load_json(self.parent.file)

        data = {
            "tytul": "mgr",
            "imie": self.imie.get(),
            "przedmiot": self.przedmiot.get(),
            "sala": self.sala.get(),
            "etap": int(self.etap.get()),
            "obecnosc": "yes",
            "moze_byc_wychowawca": self.wychowawca_var.get()
        }

        if self.mode == "add":
            nauczyciele.append(data)

        else:  # edycja
            for i, n in enumerate(nauczyciele):
                if n["imie"] == self.teacher["imie"]:
                    nauczyciele[i] = data
                    break

        save_json(self.parent.file, nauczyciele)
        self.parent.load()
        self.win.destroy()
