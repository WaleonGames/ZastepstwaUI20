#!/usr/bin/env python3
# 🎓 Generator planów lekcji v13 — dynamiczny + etapy + limity dzienne
# Autor: Kacper

import os, json, random, datetime

DATA_DIR = "data"
PLANY_DIR = os.path.join(DATA_DIR, "plany")

# === FUNKCJE ===
def load_all_json(directory):
    """Wczytuje wszystkie pliki .json z katalogu data"""
    data = {}
    for file in os.listdir(directory):
        if file.endswith(".json"):
            name = os.path.splitext(file)[0]
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

def to_minutes(t):
    return int(t.split(":")[0]) * 60 + int(t.split(":")[1])

def time_in_range(time_str, start="8:00", end="16:00"):
    """Sprawdza, czy godzina mieści się w zakresie 8:00–16:00"""
    t1, t2 = map(to_minutes, time_str.replace(" ", "").split("-"))
    s, e = to_minutes(start), to_minutes(end)
    return s <= t1 < e and s < t2 <= e

def parse_hour_range(text):
    """Zwraca listę godzin (np. '8:00-12:00') → (480, 720)"""
    try:
        s, e = text.replace(" ", "").split("-")
        return to_minutes(s), to_minutes(e)
    except:
        return 0, 1440

def class_etap(klasa, etapy):
    """Zwraca etap dla danej klasy"""
    for eid, info in etapy.items():
        if klasa in info.get("klasy", []):
            return int(eid)
    return 1

def preferowane_godziny(przedmiot):
    """Zwraca zakres godzin preferowanych"""
    zakresy = przedmiot.get("preferowane_godziny", [])
    if not zakresy:
        return [("8:00", "16:00")]
    return [tuple(z.split("-")) for z in zakresy]

# === PRZYPISYWANIE NAUCZYCIELI ===
def assign_teachers_to_classes(klasy, nauczyciele, przedmioty, etapy):
    subject_teachers = {}
    for n in nauczyciele:
        if n.get("obecnosc") == "no":
            continue
        subject_teachers.setdefault(n["przedmiot"], []).append(n)

    class_teacher_map = {}
    for klasa in klasy:
        class_teacher_map[klasa] = {}
        etap_klasy = class_etap(klasa, etapy)

        for subject, info in przedmioty.items():
            if klasa not in info["klasy"]:
                continue
            etapy_ok = info.get("etapy", [1, 2, 3])
            nauczyciele_lista = [
                n for n in subject_teachers.get(subject, [])
                if n.get("etap") in etapy_ok or n.get("etap") in (etap_klasy, 0, 1)
            ]
            if not nauczyciele_lista:
                print(f"⚠️ Brak nauczyciela {subject} dla klasy {klasa} (etap {etap_klasy})")
                continue
            chosen = random.choice(nauczyciele_lista)
            class_teacher_map[klasa][subject] = chosen
    return class_teacher_map

# === GENERATOR PLANU ===
def generate_plan(klasa, class_teachers, przedmioty, dni, godziny):
    plan = {d: [] for d in dni}
    subjects = list(class_teachers[klasa].keys())

    # Tworzymy listę wszystkich lekcji
    weekly = []
    for subj in subjects:
        hours = przedmioty[subj].get("godziny", 1)
        weekly += [subj] * hours
    random.shuffle(weekly)

    godziny = [g for g in godziny if time_in_range(g, "8:00", "16:00")]

    # licznik lekcji per subject per day
    subject_daily_count = {d: {} for d in dni}

    for dzien in dni:
        if not weekly:
            break

        # maks 5 lekcji dziennie
        daily_limit = min(len(godziny), 5)
        slots = random.sample(godziny, daily_limit)
        slots.sort(key=lambda h: godziny.index(h))

        for g in slots:
            if not weekly:
                break

            subject = weekly[0]
            max_daily = przedmioty[subject].get("lekcje_dziennie", 1)
            if subject_daily_count[dzien].get(subject, 0) >= max_daily:
                # jeśli osiągnięto dzienny limit — szukamy innego przedmiotu
                alt = next((s for s in weekly if subject_daily_count[dzien].get(s, 0) < przedmioty[s].get("lekcje_dziennie", 1)), None)
                if not alt:
                    continue
                subject = alt

            weekly.remove(subject)
            nauczyciel = class_teachers[klasa].get(subject)
            if not nauczyciel:
                continue

            subject_daily_count[dzien][subject] = subject_daily_count[dzien].get(subject, 0) + 1

            plan[dzien].append({
                "godzina": g,
                "przedmiot": subject,
                "sala": nauczyciel.get("sala", "?"),
                "nauczyciel": nauczyciel["imie"]
            })

        plan[dzien].sort(key=lambda x: godziny.index(x["godzina"]))

    return plan

# === GŁÓWNA FUNKCJA ===
def main():
    data = load_all_json(DATA_DIR)
    szkola = data.get("szkola", {})
    klasy = data.get("klasy", {})
    nauczyciele = data.get("nauczyciele", [])
    przedmioty = data.get("przedmioty", {})
    etapy = data.get("etapy", {})
    zastepstwa = data.get("zastepstwa", {})

    dni = list(zastepstwa.keys()) if zastepstwa else ["poniedzialek", "wtorek", "sroda", "czwartek", "piatek"]
    godziny = szkola.get("godziny_szkolne", [])

    godziny = [g for g in godziny if time_in_range(g, "8:00", "16:00")]
    if not godziny:
        godziny = ["8:00-8:45", "8:55-9:40", "9:50-10:35", "10:45-11:30", "11:40-12:25", "12:35-13:20"]

    print(f"🏫 Szkoła: {szkola.get('nazwa', 'Nieznana')} ({szkola.get('rok_szkolny', '-')})")
    print(f"🕗 Zakres godzin: 8:00–16:00")
    print(f"📘 Ładowanie danych: {len(przedmioty)} przedmiotów, {len(nauczyciele)} nauczycieli")

    class_teachers = assign_teachers_to_classes(klasy, nauczyciele, przedmioty, etapy)

    for klasa in klasy.keys():
        plan = generate_plan(klasa, class_teachers, przedmioty, dni, godziny)
        out_path = os.path.join(PLANY_DIR, f"{klasa}.json")
        save_json(out_path, plan)
        print(f"✅ Wygenerowano plan: {klasa} ({len(plan)} dni)")

    print("\n🎓 Wszystkie plany wygenerowane (uwzględniono limity dzienne i etapy).")

# === START ===
if __name__ == "__main__":
    main()
