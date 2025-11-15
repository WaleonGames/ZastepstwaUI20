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


class ClassesTab:
    def __init__(self, notebook, data_dir):
        self.data_dir = data_dir
        self.file = os.path.join(data_dir, "klasy.json")

        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Klasy")

        ttk.Label(frame, text="🏫 Klasy i uczniowie",
                  font=("Segoe UI", 14, "bold")).pack(pady=10)

        cols = ("klasa", "wychowawca", "uczniowie")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)

        self.tree.heading("klasa", text="Klasa")
        self.tree.heading("wychowawca", text="Wychowawca")
        self.tree.heading("uczniowie", text="Liczba uczniów")

        self.tree.column("klasa", width=80)
        self.tree.column("wychowawca", width=180)
        self.tree.column("uczniowie", width=120)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # === PODWÓJNY KLIK → PODGLĄD UCZNIÓW ===
        self.tree.bind("<Double-1>", self.show_students_window)

        # =======================
        # PRZYCISKI
        # =======================
        btn = ttk.Frame(frame)
        btn.pack(fill="x", pady=5)

        ttk.Button(btn, text="Dodaj klasę", command=self.add_class).pack(side="left", padx=5)
        ttk.Button(btn, text="Edytuj klasę", command=self.edit_class).pack(side="left", padx=5)
        ttk.Button(btn, text="Usuń klasę", command=self.delete_class).pack(side="left", padx=5)

        ttk.Button(btn, text="Dodaj ucznia", command=self.add_student).pack(side="right", padx=5)
        ttk.Button(btn, text="Usuń ucznia", command=self.delete_student).pack(side="right", padx=5)

        self.load()

    # =======================
    # ŁADOWANIE
    # =======================
    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        klasy = load_json(self.file)

        for klasa, data in klasy.items():
            self.tree.insert("", "end", values=(
                klasa,
                data.get("wychowawca", "—"),
                len(data.get("uczniowie", []))
            ))

    # =======================
    # GET SELECTED
    # =======================
    def get_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Nie wybrano klasy.")
            return None

        values = self.tree.item(sel[0])["values"]
        return values[0]   # nazwa klasy

    # =======================
    # OKNO — LISTA UCZNIÓW
    # =======================
    def show_students_window(self, event=None):
        klasa = self.get_selected()
        if not klasa:
            return

        klasy = load_json(self.file)
        uczniowie = klasy[klasa]["uczniowie"]

        win = tk.Toplevel()
        win.title(f"Uczniowie klasy {klasa}")
        win.geometry("320x420")

        ttk.Label(win, text=f"👥 Lista uczniów — {klasa}",
                  font=("Segoe UI", 13, "bold")).pack(pady=10)

        listbox = tk.Listbox(win, font=("Segoe UI", 11))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for u in uczniowie:
            listbox.insert("end", u)

        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=8)

    # =======================
    # DODAWANIE KLASY
    # =======================
    def add_class(self):
        win = tk.Toplevel()
        win.title("Dodaj klasę")
        win.geometry("300x200")

        ttk.Label(win, text="Nazwa klasy:").pack(pady=5)
        entry_class = ttk.Entry(win)
        entry_class.pack(fill="x", padx=10)

        ttk.Label(win, text="Wychowawca:").pack(pady=5)
        entry_teacher = ttk.Entry(win)
        entry_teacher.pack(fill="x", padx=10)

        def save_class():
            name = entry_class.get().strip()
            wych = entry_teacher.get().strip()

            if not name:
                messagebox.showerror("Błąd", "Klasa musi mieć nazwę!")
                return

            klasy = load_json(self.file)

            if name in klasy:
                messagebox.showerror("Błąd", "Taka klasa już istnieje!")
                return

            klasy[name] = {
                "wychowawca": wych,
                "uczniowie": []
            }

            save_json(self.file, klasy)
            self.load()
            win.destroy()

        ttk.Button(win, text="Zapisz", command=save_class).pack(pady=10)

    # =======================
    # EDYCJA KLASY
    # =======================
    def edit_class(self):
        klasa = self.get_selected()
        if not klasa:
            return

        klasy = load_json(self.file)
        data = klasy.get(klasa)

        win = tk.Toplevel()
        win.title("Edytuj klasę")
        win.geometry("300x220")

        ttk.Label(win, text=f"Nazwa klasy: {klasa}").pack(pady=5)

        ttk.Label(win, text="Wychowawca:").pack(pady=5)
        entry_teacher = ttk.Entry(win)
        entry_teacher.pack(fill="x", padx=10)
        entry_teacher.insert(0, data.get("wychowawca", ""))

        def save_edit():
            new_teacher = entry_teacher.get().strip()
            klasy[klasa]["wychowawca"] = new_teacher

            save_json(self.file, klasy)
            self.load()
            win.destroy()

        ttk.Button(win, text="Zapisz", command=save_edit).pack(pady=10)

    # =======================
    # USUWANIE KLASY
    # =======================
    def delete_class(self):
        klasa = self.get_selected()
        if not klasa:
            return

        if not messagebox.askyesno("Usuń klasę", f"Czy na pewno usunąć klasę {klasa}?"):
            return

        klasy = load_json(self.file)
        klasy.pop(klasa, None)

        save_json(self.file, klasy)
        self.load()

    # =======================
    # DODAJ UCZNIA
    # =======================
    def add_student(self):
        klasa = self.get_selected()
        if not klasa:
            return

        klasy = load_json(self.file)

        name = simpledialog.askstring("Dodaj ucznia", "Podaj imię i nazwisko ucznia:")
        if not name:
            return

        klasy[klasa]["uczniowie"].append(name)
        save_json(self.file, klasy)
        self.load()

    # =======================
    # USUŃ UCZNIA
    # =======================
    def delete_student(self):
        klasa = self.get_selected()
        if not klasa:
            return

        klasy = load_json(self.file)
        uczniowie = klasy[klasa]["uczniowie"]

        if not uczniowie:
            messagebox.showinfo("Info", "Klasa nie ma żadnych uczniów.")
            return

        # okno wyboru ucznia
        win = tk.Toplevel()
        win.title("Usuń ucznia")
        win.geometry("300x300")

        listbox = tk.Listbox(win)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)

        for u in uczniowie:
            listbox.insert("end", u)

        def remove():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]

            uczniowie.pop(idx)
            klasy[klasa]["uczniowie"] = uczniowie

            save_json(self.file, klasy)
            self.load()
            win.destroy()

        ttk.Button(win, text="Usuń", command=remove).pack(pady=10)
