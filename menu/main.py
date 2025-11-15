#!/usr/bin/env python3
# 🧰 ZastepstwaUI 2.0 — Menu główne (Python + Tkinter)
# Autor: Kacper

import sys, os

# Ustaw ROOT = katalog główny projektu
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import tkinter as tk
from tkinter import ttk, messagebox

# === Zakładki UI ===
from menu.ui.classes_tab import ClassesTab
from menu.ui.teachers_tab import TeachersTab
from menu.ui.subjects_tab import SubjectsTab
from menu.ui.plans_tab import PlansTab
from menu.ui.zast_tab import ZastepstwaTab
from menu.ui.version_manager_tab import VersionManagerTab

# === Ścieżki ===
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "..", "data")

def ensure_dirs():
    """Tworzy katalogi data/ oraz data/plany/ jeśli nie istnieją."""
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
    plany_dir = os.path.join(DATA_DIR, "plany")
    if not os.path.isdir(plany_dir):
        os.makedirs(plany_dir)


class MainApp:
    def __init__(self, root):
        self.root = root

        self.root.title("ZastepstwaUI 2.0 — Panel")
        self.root.geometry("1050x700")
        self.root.minsize(900, 600)

        # Motyw
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except:
            pass

        # === Notebook (zakładki) ===
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True)

        # === Dodanie zakładek ===
        self.load_tabs()

    def load_tabs(self):
        """Ładuje wszystkie zakładki menu."""

        ClassesTab(self.tabs, DATA_DIR)
        TeachersTab(self.tabs, DATA_DIR)
        SubjectsTab(self.tabs, DATA_DIR)
        PlansTab(self.tabs, DATA_DIR)
        ZastepstwaTab(self.tabs, DATA_DIR)
        VersionManagerTab(self.tabs, DATA_DIR)


def main():
    ensure_dirs()

    root = tk.Tk()
    app = MainApp(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Zamknięto aplikację.")


if __name__ == "__main__":
    main()
