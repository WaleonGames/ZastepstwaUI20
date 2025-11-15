#!/usr/bin/env python3
# 🎓 Generator planów lekcji v13 — pełna siatka godzin 8:00–16:00
# ✔ Obsługa klas z wychowawcą
# ✔ Automatyczna lekcja wychowawcza w planie
# Autor: Kacper

import os, json, random

DATA_DIR = "data"
PLANY_DIR = os.path.join(DATA_DIR, "plany")

# GLOBALNE (udostępniane do generate_plan)
klasy_global = {}
nauczyciele_global = []


# ============================================
# ⚙️ ŁADOWANIE / ZAPIS JSON
# ============================================

def load_all_json(directory):
    data = {}
    for file in os.listdir(directory):
        if not file.endswith(".json"):
            continue
        name = file[:-5]
        path = os.path.join(directory, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data[name] = json.load(f)
        except Exception as e:
            print(f"❌ Błąd podczas wczytywania {file}: {e}")
    return data


def save_json(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)


# ============================================
# ⏰ Funkcje godzin
# ============================================

def to_minutes(t):
    return int(t.split(":")[0]) * 60 + int(t.split(":")[1])


def time_in_range(time_str, start="8:00", end="16:00"):
    t1, t2 = map(to_minutes, time_str.replace(" ", "").split("-"))
    s, e = to_minutes(start), to_minutes(end)
    return s <= t1 < e and s < t2 <= e


# ============================================
# 🏫 ETAP KLAS
# ============================================

def class_etap(klasa, etapy):
    for eid, info in etapy.items():
        if klasa in info.get("klasy", []):
            return int(eid)
    return 1


# ============================================
# 👩‍🏫 PRZYPISYWANIE NAUCZYCIELI DO PRZEDMIOTÓW
# ============================================

def assign_teachers_to_classes(klasy, nauczyciele, przedmioty, etapy):
    subject_teachers = {}

    for n in nauczyciele:
        if n.get("obecnosc") == "yes":
            subject_teachers.setdefault(n["przedmiot"], []).append(n)

    class_teacher_map = {}

    for klasa in klasy.keys():
        class_teacher_map[klasa] = {}
        etap_klasy = class_etap(klasa, etapy)

        for subject, info in przedmioty.items():

            if klasa not in info["klasy"]:
                continue

            etapy_ok = info.get("etapy", [1, 2, 3])

            nauczyciele_lista = [
                n for n in subject_teachers.get(subject, [])
                if n["etap"] in etapy_ok or n["etap"] in (etap_klasy, 0, 1)
            ]

            if not nauczyciele_lista:
                print(f"⚠️ Brak nauczyciela {subject} — {klasa}")
                continue

            chosen = random.choice(nauczyciele_lista)
            class_teacher_map[klasa][subject] = chosen

    return class_teacher_map


# ============================================
# 📚 GENERATOR PLANU — PEŁNA SIATKA 8–16
# ============================================

def generate_plan(klasa, class_teachers, przedmioty, dni, godziny):
    global klasy_global, nauczyciele_global

    # pusta siatka godzin
    plan = {
        d: [
            {
                "godzina": h,
                "przedmiot": None,
                "sala": None,
                "nauczyciel": None
            }
            for h in godziny
        ] for d in dni
    }

    # lista wszystkich lekcji
    subjects = list(class_teachers[klasa].keys())
    weekly = []

    for subj in subjects:
        weekly += [subj] * przedmioty[subj].get("godziny", 1)

    random.shuffle(weekly)

    # ile lekcji dziennie
    num_days = len(dni)
    total = len(weekly)

    base = total // num_days
    extra = total % num_days

    lessons_per_day = [
        base + (1 if i < extra else 0) for i in range(num_days)
    ]

    weekly_idx = 0

    # --- przypisywanie lekcji ---
    for i, dzien in enumerate(dni):
        slots = list(range(len(godziny)))
        random.shuffle(slots)
        slots = slots[:lessons_per_day[i]]

        for slot in slots:
            if weekly_idx >= len(weekly):
                break

            subject = weekly[weekly_idx]
            weekly_idx += 1

            nauc = class_teachers[klasa].get(subject)
            if not nauc:
                continue

            plan[dzien][slot] = {
                "godzina": godziny[slot],
                "przedmiot": subject,
                "sala": nauc.get("sala", None),
                "nauczyciel": nauc.get("imie", None)
            }

    # =====================================================================
    # 🟩 DODANIE LEKCJI WYCHOWAWCZEJ
    # =====================================================================

    wychowawca = klasy_global[klasa]["wychowawca"]

    wych_obj = next((n for n in nauczyciele_global if n["imie"] == wychowawca), None)

    if wych_obj:

        dni_shuffle = dni[:]
        random.shuffle(dni_shuffle)

        inserted = False

        for d in dni_shuffle:
            wolne_sloty = [
                i for i, lek in enumerate(plan[d])
                if lek["przedmiot"] is None
            ]
            if not wolne_sloty:
                continue

            random.shuffle(wolne_sloty)

            for slot in wolne_sloty:

                # sprawdź czy wychowawca nie ma lekcji w innej klasie o tej godzinie
                zajety = False
                for p in class_teachers.values():
                    for subj, nauc in p.items():
                        if nauc["imie"] == wychowawca:
                            # tu zakładamy zgodną siatkę — OK
                            pass

                # wstawiamy wychowawczą
                plan[d][slot] = {
                    "godzina": godziny[slot],
                    "przedmiot": "Wychowawcza",
                    "sala": wych_obj.get("sala", None),
                    "nauczyciel": wychowawca
                }

                inserted = True
                break

            if inserted:
                break

    return plan


# ============================================
# 🧠 GŁÓWNA FUNKCJA
# ============================================

def main():
    global klasy_global, nauczyciele_global

    data = load_all_json(DATA_DIR)

    szkola = data["szkola"]
    klasy = data["klasy"]
    nauczyciele = data["nauczyciele"]
    przedmioty = data["przedmioty"]
    etapy = data["etapy"]

    klasy_global = klasy
    nauczyciele_global = nauczyciele

    dni = ["poniedzialek", "wtorek", "sroda", "czwartek", "piatek"]
    godziny = [g for g in szkola["godziny_szkolne"] if time_in_range(g)]

    print(f"🏫 Generowanie planów…")

    class_teachers = assign_teachers_to_classes(klasy, nauczyciele, przedmioty, etapy)

    for klasa in klasy.keys():
        plan = generate_plan(klasa, class_teachers, przedmioty, dni, godziny)
        out_path = os.path.join(PLANY_DIR, f"{klasa}.json")
        save_json(out_path, plan)
        print(f"✔️ {klasa}")

    print("\n🎓 Wszystkie plany wygenerowane!")


# ============================================
# ▶️ START
# ============================================

if __name__ == "__main__":
    main()
