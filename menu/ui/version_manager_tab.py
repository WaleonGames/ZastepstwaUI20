import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from io import BytesIO

from menu.utils.version_manager_utils import (
    load_local_version,
    fetch_latest_release,
    download_zip,
    install_zip
)


class VersionManagerTab:
    def __init__(self, notebook, data_dir):
        self.base_dir = os.path.abspath(os.path.join(data_dir, ".."))
        self.data_dir = data_dir
        self.version_file = os.path.join(data_dir, "version.json")

        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Aktualizacje")

        ttk.Label(frame, text="🔧 Menedżer aktualizacji",
                  font=("Segoe UI", 14, "bold")).pack(pady=10)

        # --- INFORMACJE ---
        info_box = ttk.LabelFrame(frame, text="Informacje o wersji")
        info_box.pack(fill="x", padx=10, pady=5)

        self.local_version_lbl = ttk.Label(info_box, text="Aktualna wersja: —")
        self.local_version_lbl.pack(anchor="w", padx=10, pady=2)

        self.remote_version_lbl = ttk.Label(info_box, text="Najnowsza wersja: —")
        self.remote_version_lbl.pack(anchor="w", padx=10, pady=2)

        # --- PRZYCISKI ---
        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=5)

        ttk.Button(
            btns, text="🔍 Sprawdź aktualizację",
            command=self.check_update
        ).pack(side="left", padx=5)

        ttk.Button(
            btns, text="⬇ Pobierz i zainstaluj",
            command=self.update_now
        ).pack(side="left", padx=5)

        ttk.Button(
            btns, text="📦 Zainstaluj z pliku .zip",
            command=self.install_from_zip
        ).pack(side="left", padx=5)

        # --- CHANGELOG ---
        ttk.Label(frame, text="📄 Changelog", font=("Segoe UI", 11, "bold")).pack(pady=(5, 0))

        self.changelog = scrolledtext.ScrolledText(frame, height=12, font=("Consolas", 9))
        self.changelog.pack(fill="both", expand=True, padx=10, pady=10)

        # Ładujemy wersję lokalną z JSON
        self.load_local_version()

    # ===============================
    # ŁADOWANIE WERSJI LOKALNEJ
    # ===============================
    def load_local_version(self):
        version = load_local_version(self.version_file)
        self.local_version_lbl.config(text=f"Aktualna wersja: {version}")

    # ===============================
    # SPRAWDZANIE AKTUALIZACJI
    # ===============================
    def check_update(self):
        self.changelog.delete(1.0, "end")

        data = fetch_latest_release()

        if "error" in data:
            messagebox.showerror("Błąd", f"Nie udało się pobrać danych:\n{data['error']}")
            return

        self.remote_version = data["version"]
        self.remote_url = data["zip_url"]
        self.remote_body = data["body"]

        self.remote_version_lbl.config(text=f"Najnowsza wersja: {self.remote_version}")
        self.changelog.insert("end", data["body"])

    # ===============================
    # AKTUALIZACJA Z GITHUB
    # ===============================
    def update_now(self):
        if not getattr(self, "remote_url", None):
            messagebox.showwarning("Brak danych", "Kliknij najpierw: Sprawdź aktualizację")
            return

        zip_bytes = download_zip(self.remote_url)
        if not zip_bytes:
            messagebox.showerror("Błąd", "Nie udało się pobrać ZIP aktualizacji.")
            return

        ok = install_zip(zip_bytes, self.base_dir)

        if ok:
            messagebox.showinfo("Sukces", "Aktualizacja została zainstalowana.")

            # Wczytaj wersję z nowego version.json
            self.load_local_version()

            self.changelog.insert("end", "\n\n[✔] Instalacja zakończona")
        else:
            messagebox.showerror("Błąd", "Nie udało się rozpakować ZIP.")

    # ===============================
    # INSTALACJA RĘCZNEGO ZIP
    # ===============================
    def install_from_zip(self):
        path = filedialog.askopenfilename(
            title="Wybierz plik ZIP",
            filetypes=[("Paczek ZIP", "*.zip")]
        )

        if not path:
            return

        try:
            with open(path, "rb") as f:
                zip_bytes = BytesIO(f.read())
        except:
            messagebox.showerror("Błąd", "Nie można odczytać pliku ZIP.")
            return

        ok = install_zip(zip_bytes, self.base_dir)

        if ok:
            messagebox.showinfo("Sukces", "Ręczna instalacja zakończona.")

            # Pobierz wersję z nowego version.json
            self.load_local_version()

        else:
            messagebox.showerror("Błąd", "Nie udało się zainstalować ZIP.")
