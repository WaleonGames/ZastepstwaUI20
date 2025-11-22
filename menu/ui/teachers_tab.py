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
        cols = (
            "imie", "przedmiot", "sala", "etap",
            "klasy", "specjalizacja",
            "obecnosc", "powod", "wychowawca"
        )

        self.tree = ttk.Treeview(
            self.frame,
            columns=cols,
            show="headings",
            height=18,
            selectmode="extended"  # 🔥 MULTI-SELECT
        )
        self.tree.pack(fill="both", expand=True, padx=10)

        headers = {
            "imie": "Imię i nazwisko",
            "przedmiot": "Przedmiot",
            "sala": "Sala",
            "etap": "Etap",
            "klasy": "Klasy",
            "specjalizacja": "Specjalizacja",
            "obecnosc": "Obecność",
            "powod": "Powód",
            "wychowawca": "Wychowawca?"
        }

        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=140)

        # ============================
        # MENU PPM
        # ============================
        self.menu = tk.Menu(self.frame, tearoff=0)
        self.menu.add_command(label="Edytuj", command=self.edit)
        self.menu.add_command(label="Usuń", command=self.delete_multiple)
        self.menu.add_separator()
        self.menu.add_command(label="Zmień status", command=self.toggle_status_multiple)
        self.menu.add_command(label="Ustaw powód nieobecności", command=self.set_reason_multiple)

        self.tree.bind("<Button-3>", self.show_context_menu)

        # ============================
        # Przyciski klasyczne
        # ============================
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Dodaj", command=self.add).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj", command=self.edit).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Usuń", command=self.delete_multiple).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Zmień status", command=self.toggle_status_multiple).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Powód nieobecności", command=self.set_reason_multiple).pack(side="left", padx=5)

        self.load()

    # ==================================================
    # MENU PRAWEGO KLIKNIĘCIA
    # ==================================================
    def show_context_menu(self, event):
        row = self.tree.identify_row(event.y)

        # jeśli kliknięto na wiersz...
        if row:
            # jeśli wiersz NIE jest zaznaczony → zaznacz tylko jego
            # (bo użytkownik chce zmienić wybór)
            if row not in self.tree.selection():
                self.tree.selection_set(row)
            # jeśli już był zaznaczony → NIE ZMIENIAMY ZAZNACZENIA
            # (multiselect zostaje)
        else:
            return  # klik pusty – brak menu

        # ile jest zaznaczonych?
        count = len(self.tree.selection())

        # dynamiczne etykiety
        self.menu.entryconfig(0, label="Edytuj" + (" (1)" if count == 1 else " (tylko 1)"))
        self.menu.entryconfig(1, label=f"Usuń ({count})")
        self.menu.entryconfig(3, label=f"Zmień status ({count})")
        self.menu.entryconfig(4, label=f"Ustaw powód ({count})")

        # pokaż menu
        self.menu.tk_popup(event.x_root, event.y_root)

    # ==================================================
    # Pobranie jednego zaznaczonego nauczyciela
    # ==================================================
    def get_selected(self):
        sel = self.tree.selection()
        if len(sel) != 1:
            messagebox.showwarning("Błąd", "Zaznacz dokładnie jednego nauczyciela.")
            return None

        v = self.tree.item(sel[0])["values"]

        return {
            "imie": v[0],
            "przedmiot": v[1],
            "sala": v[2],
            "etap": v[3],
            "klasy": v[4],
            "specjalizacja": v[5],
            "obecnosc": "yes" if v[6] == "Obecny" else "no",
            "powod": v[7],
            "moze_byc_wychowawca": True if v[8] == "TAK" else False
        }

    # ==================================================
    # Pobranie wielu zaznaczonych nauczycieli
    # ==================================================
    def get_selected_multiple(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Nie wybrano nauczycieli.")
            return None

        teachers = []
        for s in sel:
            v = self.tree.item(s)["values"]
            teachers.append({
                "imie": v[0],
                "przedmiot": v[1],
                "sala": v[2],
                "etap": v[3],
                "klasy": v[4],
                "specjalizacja": v[5],
                "obecnosc": "yes" if v[6] == "Obecny" else "no",
                "powod": v[7],
                "moze_byc_wychowawca": True if v[8] == "TAK" else False
            })

        return teachers

    # ==================================================
    # Ładowanie tabeli
    # ==================================================
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for n in load_json(self.file):
            self.tree.insert("", "end", values=(
                n.get("imie"),
                n.get("przedmiot"),
                n.get("sala"),
                n.get("etap"),
                ", ".join(n.get("klasy", [])),
                n.get("specjalizacja", ""),
                "Obecny" if n.get("obecnosc") == "yes" else "Nieobecny",
                n.get("powod", "") if n.get("obecnosc") == "no" else "",
                "TAK" if n.get("moze_byc_wychowawca") else "NIE"
            ))

    # ==================================================
    # Dodawanie
    # ==================================================
    def add(self):
        AddEditTeacher(self, "add")

    # ==================================================
    # Edycja
    # ==================================================
    def edit(self):
        teacher = self.get_selected()
        if teacher:
            AddEditTeacher(self, "edit", teacher)

    # ==================================================
    # Usuwanie wielu
    # ==================================================
    def delete_multiple(self):
        teachers = self.get_selected_multiple()
        if not teachers:
            return

        names = "\n".join(t["imie"] for t in teachers)

        if not messagebox.askyesno("Potwierdź usunięcie",
                                   f"Czy chcesz usunąć nauczycieli:\n\n{names}\n"):
            return

        data = load_json(self.file)
        selected_names = {t["imie"] for t in teachers}

        data = [n for n in data if n["imie"] not in selected_names]

        save_json(self.file, data)
        self.load()

    # ==================================================
    # Zmiana statusu dla wielu
    # ==================================================
    def toggle_status_multiple(self):
        teachers = self.get_selected_multiple()
        if not teachers:
            return

        data = load_json(self.file)

        for t in teachers:
            for n in data:
                if n["imie"] == t["imie"]:
                    if n["obecnosc"] == "yes":
                        n["obecnosc"] = "no"
                        n["powod"] = "Brak powodu"
                    else:
                        n["obecnosc"] = "yes"
                        n.pop("powod", None)
                    break

        save_json(self.file, data)
        self.load()

    # ==================================================
    # Powód dla wielu
    # ==================================================
    def set_reason_multiple(self):
        teachers = self.get_selected_multiple()
        if not teachers:
            return

        nieobecni = [t for t in teachers if t["obecnosc"] == "no"]

        if not nieobecni:
            messagebox.showinfo("Brak",
                                "Wszyscy wybrani nauczyciele są obecni.")
            return

        reason = simpledialog.askstring("Powód nieobecności", "Podaj powód:")
        if not reason:
            return

        data = load_json(self.file)

        for t in nieobecni:
            for n in data:
                if n["imie"] == t["imie"]:
                    n["powod"] = reason
                    break

        save_json(self.file, data)
        self.load()


# ==================================================
# OKNO Dodawania / Edycji
# ==================================================
class AddEditTeacher:
    def __init__(self, parent, mode, teacher=None):
        self.parent = parent
        self.mode = mode
        self.teacher = teacher

        self.win = tk.Toplevel()
        self.win.title("Dodaj nauczyciela" if mode == "add" else "Edytuj nauczyciela")
        self.win.geometry("360x520")
        self.win.resizable(False, False)

        # Pola
        ttk.Label(self.win, text="Imię i nazwisko:").pack()
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

        ttk.Label(self.win, text="Klasy (np. 1A,2B):").pack()
        self.klasy = ttk.Entry(self.win)
        self.klasy.pack(fill="x", padx=10, pady=4)

        ttk.Label(self.win, text="Specjalizacja:").pack()
        self.specjalizacja = ttk.Entry(self.win)
        self.specjalizacja.pack(fill="x", padx=10, pady=4)

        self.wychowawca_var = tk.BooleanVar()
        ttk.Checkbutton(self.win,
                        text="Może być wychowawcą",
                        variable=self.wychowawca_var).pack(pady=6)

        ttk.Button(self.win, text="Zapisz", command=self.save).pack(pady=10)

        if mode == "edit":
            self.imie.insert(0, teacher["imie"])
            self.przedmiot.insert(0, teacher["przedmiot"])
            self.sala.insert(0, teacher["sala"])
            self.etap.insert(0, teacher["etap"])
            self.klasy.insert(0, teacher["klasy"])
            self.specjalizacja.insert(0, teacher["specjalizacja"])
            self.wychowawca_var.set(teacher["moze_byc_wychowawca"])

    def save(self):
        data = load_json(self.parent.file)

        entry = {
            "imie": self.imie.get(),
            "przedmiot": self.przedmiot.get(),
            "sala": self.sala.get(),
            "etap": self.etap.get(),
            "klasy": [k.strip() for k in self.klasy.get().split(",") if k.strip()],
            "specjalizacja": self.specjalizacja.get(),
            "obecnosc": "yes",
            "moze_byc_wychowawca": self.wychowawca_var.get()
        }

        if self.mode == "add":
            data.append(entry)
        else:
            for i, n in enumerate(data):
                if n["imie"] == self.teacher["imie"]:
                    data[i] = entry
                    break

        save_json(self.parent.file, data)
        self.parent.load()
        self.win.destroy()
