#!/usr/bin/env python3
# 🎓 Generator planów lekcji v8 — stały nauczyciel + realistyczne rozłożenie godzin + obecnosc
# Autor: Kacper

import json, os, random

# === STAŁE ===
DATA_DIR = "data"
PLANY_DIR = os.path.join(DATA_DIR, "plany")
DNI = ["poniedzialek", "wtorek", "sroda", "czwartek", "piatek"]
GODZINY = [
    "8:00 - 8:45",
    "8:55 - 9:40",
    "9:50 - 10:35",
    "10:45 - 11:30",
    "11:40 - 12:25",
    "12:35 - 13:20"
]

# === FUNKCJE POMOCNICZE ===
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === PRZYPISYWANIE NAUCZYCIELI DO KLAS ===
def assign_teachers_to_classes(klasy, nauczyciele, przedmioty):
    """Każda klasa ma przypisanego jednego obecnego nauczyciela dla danego przedmiotu."""
    subject_teachers = {}

    # grupowanie nauczycieli wg przedmiotów i obecności
    for n in nauczyciele:
        if n.get("obecnosc") == "no":
            continue  # pomijamy nieobecnych
        subject_teachers.setdefault(n["przedmiot"], []).append(n)

    class_teacher_map = {}
    for klasa in klasy:
        class_teacher_map[klasa] = {}
        for subject, info in przedmioty.items():
            if klasa not in info["klasy"]:
                continue

            nauczyciele_lista = subject_teachers.get(subject, [])
            if not nauczyciele_lista:
                print(f"⚠️ Brak dostępnych nauczycieli dla przedmiotu {subject} w klasie {klasa}")
                continue

            chosen = random.choice(nauczyciele_lista)
            class_teacher_map[klasa][subject] = chosen

    return class_teacher_map

# === GENERATOR PLANU DLA KLASY ===
def generate_plan_for_class(klasa, class_teachers, przedmioty, all_busy=None):
    if all_busy is None:
        all_busy = {n["imie"]: {d: [] for d in DNI} for n in sum(
            [list(v.values()) for v in class_teachers.values()], []
        )}

    plan = {d: [] for d in DNI}
    subjects = list(class_teachers[klasa].keys())

    # lista lekcji w tygodniu (na podstawie liczby godzin)
    weekly_subjects = []
    for subj in subjects:
        hours = przedmioty[subj]["godziny"]
        weekly_subjects.extend([subj] * hours)
    random.shuffle(weekly_subjects)

    # rozdzielamy lekcje równomiernie na dni
    day_count = len(DNI)
    for dzien in DNI:
        daily_lessons = min(5, max(3, len(weekly_subjects) // day_count))
        chosen_subjects = weekly_subjects[:daily_lessons]
        weekly_subjects = weekly_subjects[daily_lessons:]

        # wybieramy godziny ciągiem
        start_index = random.randint(0, max(0, len(GODZINY) - daily_lessons))
        godziny_dnia = GODZINY[start_index:start_index + daily_lessons]

        for i, subject in enumerate(chosen_subjects):
            nauczyciel = class_teachers[klasa].get(subject)
            if not nauczyciel:
                continue  # brak przypisanego nauczyciela
            godzina = godziny_dnia[i]

            # sprawdzenie kolizji
            if godzina in all_busy[nauczyciel["imie"]][dzien]:
                continue

            all_busy[nauczyciel["imie"]][dzien].append(godzina)
            plan[dzien].append({
                "godzina": godzina,
                "przedmiot": subject,
                "sala": nauczyciel["sala"],
                "nauczyciel": nauczyciel["imie"]
            })

        plan[dzien].sort(key=lambda x: GODZINY.index(x["godzina"]))

    return plan, all_busy

# === GŁÓWNA FUNKCJA ===
def main():
    klasy_path = os.path.join(DATA_DIR, "klasy.json")
    nauczyciele_path = os.path.join(DATA_DIR, "nauczyciele.json")
    przedmioty_path = os.path.join(DATA_DIR, "przedmioty.json")

    if not (os.path.exists(klasy_path) and os.path.exists(nauczyciele_path) and os.path.exists(przedmioty_path)):
        print("❌ Brak jednego z plików: klasy.json / nauczyciele.json / przedmioty.json")
        return

    klasy = load_json(klasy_path)
    nauczyciele = load_json(nauczyciele_path)
    przedmioty = load_json(przedmioty_path)

    print("📚 Generowanie planów lekcji z uwzględnieniem obecności nauczycieli...")

    # przypisanie nauczycieli
    class_teachers = assign_teachers_to_classes(klasy, nauczyciele, przedmioty)

    # globalna kontrola zajętości nauczycieli
    all_busy = {n["imie"]: {d: [] for d in DNI} for n in nauczyciele}

    # generowanie planów
    for klasa in klasy.keys():
        plan, all_busy = generate_plan_for_class(klasa, class_teachers, przedmioty, all_busy=all_busy)
        output_path = os.path.join(PLANY_DIR, f"{klasa.upper()}.json")
        save_json(output_path, plan)
        print(f"✅ {klasa.upper()} — zapisano plan ({len(plan)} dni)")

    print("\n🎓 Wszystkie plany wygenerowane pomyślnie (tylko obecni nauczyciele)!")

# === START ===
if __name__ == "__main__":
    main()
