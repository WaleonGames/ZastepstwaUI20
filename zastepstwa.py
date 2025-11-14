#!/usr/bin/env python3
# 🧑‍🏫 Generator zastępstw v7 — faktyczne nieobecności z nauczyciele.json
# Autor: Kacper

import json, os, re

DATA_DIR = "data"
PLANY_DIR = os.path.join(DATA_DIR, "plany")
OUTPUT_PATH = os.path.join(DATA_DIR, "zastepstwa.json")

DNI = ["poniedzialek", "wtorek", "sroda", "czwartek", "piatek"]

# === FUNKCJE ===
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_rocznik(klasa):
    match = re.match(r"(\d+)", klasa)
    return match.group(1) if match else None

# === GŁÓWNA FUNKCJA ===
def main():
    nauczyciele = load_json(os.path.join(DATA_DIR, "nauczyciele.json"))
    klasy = [f[:-5] for f in os.listdir(PLANY_DIR) if f.endswith(".json")]
    plany = {k: load_json(os.path.join(PLANY_DIR, f"{k}.json")) for k in klasy}

    zastepstwa = {d: [] for d in DNI}

    # 🧾 lista faktycznie nieobecnych z pliku nauczyciele.json
    nieobecni = [n for n in nauczyciele if n["obecnosc"] == "no"]
    obecni = [n for n in nauczyciele if n["obecnosc"] == "yes"]

    if not nieobecni:
        print("ℹ️ Brak nieobecności — wszyscy nauczyciele obecni.")
        save_json(OUTPUT_PATH, {d: [] for d in DNI})
        return

    print(f"🔍 Generowanie zastępstw (v7 — {len(nieobecni)} faktycznych nieobecnych)...")

    for n in nieobecni:
        imie = n["imie"]
        przedmiot = n["przedmiot"]
        powod = n.get("powod", "brak informacji")

        print(f"\n🚫 {imie} — nieobecny ({powod})")

        # przejrzyj wszystkie klasy i dni
        for klasa, plan in plany.items():
            for dzien, lekcje in plan.items():
                for lekcja in lekcje:
                    if lekcja["nauczyciel"] != imie:
                        continue

                    godzina = lekcja["godzina"]
                    rocznik = extract_rocznik(klasa)
                    status = "odwołane"
                    nauczyciel_zast = None
                    opis = f"Zajęcia odwołane ({powod})"

                    # === 1️⃣ Łączenie klas tego samego rocznika ===
                    polaczone_z = None
                    for inna_klasa, plan_inny in plany.items():
                        if inna_klasa == klasa:
                            continue
                        if extract_rocznik(inna_klasa) == rocznik:
                            for lekcja_inna in plan_inny.get(dzien, []):
                                if lekcja_inna["godzina"] == godzina:
                                    polaczone_z = inna_klasa
                                    status = "łączenie"
                                    nauczyciel_zast = lekcja_inna["nauczyciel"]
                                    opis = f"Połączono klasy {klasa} i {inna_klasa} ({powod})"
                                    break
                        if polaczone_z:
                            break

                    # === 2️⃣ Zastępstwo — wolny nauczyciel ===
                    if not polaczone_z:
                        wolni = []
                        for kandydat in obecni:
                            zajety = any(
                                l["nauczyciel"] == kandydat["imie"] and l["godzina"] == godzina
                                for p in plany.values()
                                for lekcje_dnia in p.values()
                                for l in lekcje_dnia
                            )
                            if not zajety and kandydat["imie"] != imie:
                                wolni.append(kandydat)

                        if wolni:
                            wybrany = wolni[0]  # pierwszy wolny zamiast random
                            status = "zastępstwo"
                            nauczyciel_zast = wybrany["imie"]
                            opis = f"Zastępuje {wybrany['imie']} ({wybrany['przedmiot']}) — {powod}"

                    zastepstwa[dzien].append({
                        "godzina": godzina,
                        "klasa": klasa,
                        "przedmiot": lekcja["przedmiot"],
                        "nauczyciel_nieobecny": imie,
                        "nauczyciel_zastepujacy": nauczyciel_zast,
                        "status": status,
                        "opis": opis
                    })

    save_json(OUTPUT_PATH, zastepstwa)

    total = sum(len(zastepstwa[d]) for d in DNI)
    if total == 0:
        print("\nℹ️ Brak lekcji nieobecnych nauczycieli w planach.")
    else:
        stat = {"łączenie": 0, "zastępstwo": 0, "odwołane": 0}
        for d in DNI:
            for z in zastepstwa[d]:
                stat[z["status"]] += 1

        print(f"\n✅ Zapisano: {OUTPUT_PATH}")
        print(f"📊 Łącznie: {total} — łączeń: {stat['łączenie']}, zastępstw: {stat['zastępstwo']}, odwołanych: {stat['odwołane']}")

# === START ===
if __name__ == "__main__":
    main()
