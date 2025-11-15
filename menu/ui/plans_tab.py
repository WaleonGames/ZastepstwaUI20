import os
import json
import subprocess
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


class PlansTab:
    def __init__(self, notebook, data_dir):
        self.data_dir = data_dir
        self.plany_dir = os.path.join(data_dir, "plany")

        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Plany lekcji")

        ttk.Label(
            frame,
            text="🗓 Wygenerowane plany lekcji",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        # ================================
        # TABELA
        # ================================
        cols = ("klasa", "dni")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=18)

        self.tree.heading("klasa", text="Plik (klasa)")
        self.tree.heading("dni", text="Ilość dni")

        self.tree.column("klasa", width=180)
        self.tree.column("dni", width=100)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # ================================
        # PRZYCISKI — CRUD + GENERATOR
        # ================================
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=8)

        # LEWA STRONA
        ttk.Button(btn_frame, text="Podgląd", command=self.preview_plan).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Edytuj plan", command=self.edit_plan).pack(side="left", padx=5)

        # PRAWA STRONA
        ttk.Button(btn_frame, text="Dodaj nowy plan", command=self.add_plan).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Usuń plan", command=self.delete_plan).pack(side="right", padx=5)

        # ================================
        # PRZYCISKI — GENERATOR PLANÓW
        # ================================
        gen_frame = ttk.Frame(frame)
        gen_frame.pack(fill="x", pady=5)

        ttk.Button(
            gen_frame,
            text="🔄 Generuj plany lekcji",
            command=self.generate_plans
        ).pack(side="left", padx=5)

        # double click → edytuj
        self.tree.bind("<Double-1>", lambda e: self.edit_plan())

        self.load()

    # ============================================
    # ŁADOWANIE LISTY PLANÓW
    # ============================================
    def load(self):
        if not os.path.isdir(self.plany_dir):
            return

        for row in self.tree.get_children():
            self.tree.delete(row)

        for file in os.listdir(self.plany_dir):
            if file.endswith(".json"):
                path = os.path.join(self.plany_dir, file)
                plan = load_json(path)

                klasa = file.replace(".json", "")
                dni = len(plan.keys())

                self.tree.insert("", "end", values=(klasa, dni))

    # ============================================
    # DODAJ PUSTY PLAN
    # ============================================
    def add_plan(self):
        name = simpledialog.askstring("Nowy plan", "Podaj nazwę klasy (np. 1A):")
        if not name:
            return

        path = os.path.join(self.plany_dir, f"{name}.json")

        if os.path.exists(path):
            messagebox.showerror("Błąd", "Plan tej klasy już istnieje.")
            return

        empty = {
            "poniedzialek": [],
            "wtorek": [],
            "sroda": [],
            "czwartek": [],
            "piatek": []
        }

        save_json(path, empty)
        self.load()

        messagebox.showinfo("OK", f"Utworzono pusty plan dla klasy {name}")

    # ============================================
    # PODGLĄD PLANU
    # ============================================
    def preview_plan(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Nie wybrano planu.")
            return

        klasa = self.tree.item(sel[0])["values"][0]
        self.open_plan_window(klasa, editable=False)

    # ============================================
    # EDYCJA PLANU
    # ============================================
    def edit_plan(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Nie wybrano planu.")
            return

        klasa = self.tree.item(sel[0])["values"][0]
        self.open_plan_window(klasa, editable=True)

    # ============================================
    # OKNO PODGLĄDU / EDYCJI
    # ============================================
    def open_plan_window(self, klasa, editable=False):
        path = os.path.join(self.plany_dir, f"{klasa}.json")
        plan = load_json(path)

        win = tk.Toplevel()
        win.title(f"Plan lekcji — {klasa}")
        win.geometry("850x550")

        ttk.Label(
            win,
            text=f"Plan lekcji — klasa {klasa}",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        cols = ("dzien", "godzina", "przedmiot", "nauczyciel", "sala")

        table = ttk.Treeview(win, columns=cols, show="headings", height=20)

        for c in cols:
            table.heading(c, text=c.capitalize())

        table.column("dzien", width=120)
        table.column("godzina", width=120)
        table.column("przedmiot", width=150)
        table.column("nauczyciel", width=150)
        table.column("sala", width=100)

        table.pack(fill="both", expand=True, padx=10, pady=10)

        # Wczytaj lekcje
        for dzien, lekcje in plan.items():
            for lekcja in lekcje:
                table.insert("", "end", values=(
                    dzien,
                    lekcja.get("godzina"),
                    lekcja.get("przedmiot"),
                    lekcja.get("nauczyciel"),
                    lekcja.get("sala")
                ))

        # PRZYCISKI EDYCJI
        if editable:
            btn = ttk.Frame(win)
            btn.pack(fill="x", pady=5)

            ttk.Button(btn, text="Dodaj lekcję",
                       command=lambda: self.add_lesson(table, klasa)).pack(side="left", padx=5)

            ttk.Button(btn, text="Edytuj lekcję",
                       command=lambda: self.edit_lesson(table, klasa)).pack(side="left", padx=5)

            ttk.Button(btn, text="Usuń lekcję",
                       command=lambda: self.delete_lesson(table, klasa)).pack(side="left", padx=5)

        ttk.Button(win, text="Zamknij", command=win.destroy).pack(pady=10)

    # ============================================
    # DODAJ LEKCJĘ
    # ============================================
    def add_lesson(self, table, klasa):
        path = os.path.join(self.plany_dir, f"{klasa}.json")
        plan = load_json(path)

        win = tk.Toplevel()
        win.title("Dodaj lekcję")
        win.geometry("350x350")

        ttk.Label(win, text="Dzień tygodnia:").pack(pady=5)
        day = ttk.Combobox(win, values=list(plan.keys()))
        day.pack(fill="x", padx=10)

        ttk.Label(win, text="Godzina (np. 8:00-8:45):").pack(pady=5)
        e1 = ttk.Entry(win)
        e1.pack(fill="x", padx=10)

        ttk.Label(win, text="Przedmiot:").pack(pady=5)
        e2 = ttk.Entry(win)
        e2.pack(fill="x", padx=10)

        ttk.Label(win, text="Nauczyciel:").pack(pady=5)
        e3 = ttk.Entry(win)
        e3.pack(fill="x", padx=10)

        ttk.Label(win, text="Sala:").pack(pady=5)
        e4 = ttk.Entry(win)
        e4.pack(fill="x", padx=10)

        def save_new():
            d = day.get()
            if not d:
                return

            new_lesson = {
                "godzina": e1.get(),
                "przedmiot": e2.get(),
                "nauczyciel": e3.get(),
                "sala": e4.get()
            }

            plan[d].append(new_lesson)
            save_json(path, plan)

            table.insert("", "end", values=(d, *new_lesson.values()))
            win.destroy()

        ttk.Button(win, text="Zapisz", command=save_new).pack(pady=10)

    # ============================================
    # EDYCJA LEKCJI
    # ============================================
    def edit_lesson(self, table, klasa):
        sel = table.selection()
        if not sel:
            messagebox.showerror("Błąd", "Nie wybrano lekcji.")
            return

        values = table.item(sel[0])["values"]
        dzien, godzina, przedmiot, nauczyciel, sala = values

        path = os.path.join(self.plany_dir, f"{klasa}.json")
        plan = load_json(path)

        win = tk.Toplevel()
        win.title("Edytuj lekcję")
        win.geometry("350x350")

        ttk.Label(win, text=f"Dzień: {dzien}").pack(pady=5)

        ttk.Label(win, text="Godzina:").pack(pady=5)
        e1 = ttk.Entry(win)
        e1.pack(fill="x", padx=10)
        e1.insert(0, godzina)

        ttk.Label(win, text="Przedmiot:").pack(pady=5)
        e2 = ttk.Entry(win)
        e2.pack(fill="x", padx=10)
        e2.insert(0, przedmiot)

        ttk.Label(win, text="Nauczyciel:").pack(pady=5)
        e3 = ttk.Entry(win)
        e3.pack(fill="x", padx=10)
        e3.insert(0, nauczyciel)

        ttk.Label(win, text="Sala:").pack(pady=5)
        e4 = ttk.Entry(win)
        e4.pack(fill="x", padx=10)
        e4.insert(0, sala)

        def save_edit():
            for lesson in plan[dzien]:
                if lesson["godzina"] == godzina:
                    lesson["godzina"] = e1.get()
                    lesson["przedmiot"] = e2.get()
                    lesson["nauczyciel"] = e3.get()
                    lesson["sala"] = e4.get()
                    break

            save_json(path, plan)
            self.load()
            win.destroy()

        ttk.Button(win, text="Zapisz", command=save_edit).pack(pady=10)

    # ============================================
    # USUŃ LEKCJĘ (ustaw na null)
    # ============================================
    def delete_lesson(self, table, klasa):
        sel = table.selection()
        if not sel:
            messagebox.showerror("Błąd", "Nie wybrano lekcji.")
            return

        values = table.item(sel[0])["values"]
        dzien, godzina, p, n, s = values

        if not messagebox.askyesno(
            "Usuń lekcję",
            f"Czy na pewno usunąć lekcję o {godzina}?\nWartości zostaną ustawione na null."
        ):
            return

        path = os.path.join(self.plany_dir, f"{klasa}.json")
        plan = load_json(path)

        # wyczyść lekcję
        for lesson in plan[dzien]:
            if lesson["godzina"] == godzina:
                lesson["przedmiot"] = None
                lesson["nauczyciel"] = None
                lesson["sala"] = None
                break

        save_json(path, plan)

        table.item(sel[0], values=(dzien, godzina, None, None, None))

    # ============================================
    # USUŃ CAŁY PLAN
    # ============================================
    def delete_plan(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Błąd", "Nie wybrano planu.")
            return

        klasa = self.tree.item(sel[0])["values"][0]
        path = os.path.join(self.plany_dir, f"{klasa}.json")

        if not messagebox.askyesno("Usuń plan", f"Usunąć plan dla klasy {klasa}?"):
            return

        try:
            os.remove(path)
            self.load()
            messagebox.showinfo("OK", "Plan usunięty.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można usunąć pliku:\n{e}")

    # ============================================
    # GENERATOR PLANÓW LEKCJI (plans.py)
    # ============================================
    def generate_plans(self):

        script = os.path.join(os.path.dirname(self.data_dir), "plans.py")

        if not os.path.exists(script):
            messagebox.showerror("Błąd", f"Nie znaleziono generatora:\n{script}")
            return

        try:
            result = subprocess.run(
                ["python3", script],
                cwd=os.path.dirname(self.data_dir),
                capture_output=True,
                text=True
            )

            # DEBUG - możesz zobaczyć log w terminalu
            print(result.stdout)
            print(result.stderr)

            self.load()
            messagebox.showinfo("Gotowe!", "Plany lekcji zostały wygenerowane ✔")

        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się uruchomić generatora:\n{e}")
