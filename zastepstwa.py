#!/usr/bin/env python3
# 🧑‍🏫 Generator zastępstw v5 — faktyczna nieobecność nauczycieli (z dniami i powodem)
# Autor: Kacper

import json, os, random, re

DATA_DIR = "data"
PLANY_DIR = os.path.join(DATA_DIR, "plany")
OUTPUT_PATH = os.path.join(DATA_DIR, "zastepstwa.json")

DNI = ["poniedzialek", "wtorek", "sroda", "czwartek", "piatek"]

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

def main():
    nauczyciele = load_json(os.path.join(DATA_DIR, "nauczyciele.json"))
    klasy = [f[:-5] for f in os.listdir(PLANY_DIR) if f.endswith(".json")]
    plany = {k: load_json(os.path.join(PLANY_DIR, f"{k}.json")) for k in klasy}

    zastepstwa = {d: [] for d in DNI}

    nauczyciele_obecni = [n for n in nauczyciele if n["obecnosc"] == "yes"]

    print("🔍 Generowanie zastępstw (v5 – faktyczna nieobecność)...")

    for n in nauczyciele:
        if n["obecnosc"] != "no":
            continue

        imie = n["imie"]
        przedmiot = n["przedmiot"]
        powod = n.get("powod", "brak informacji")
        dni_nieob = n.get("dni_nieobecnosci", random.randint(1, 3))
        dni_nieobecne = random.sample(DNI, min(dni_nieob, len(DNI)))

        print(f"🚫 {imie} — nieobecny {dni_nieob} dni ({', '.join(dni_nieobecne)}), powód: {powod}")

        # dla każdego dnia nieobecności generujemy zastępstwa
        for dzien in dni_nieobecne:
            for klasa, plan in plany.items():
                if dzien not in plan:
                    continue
                for lekcja in plan[dzien]:
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

                    # === 2️⃣ Wolny nauczyciel (jeśli brak połączenia) ===
                    if not polaczone_z:
                        wolni = []
                        for kandydat in nauczyciele_obecni:
                            zajety = False
                            for p in plany.values():
                                for lekcje_dnia in p.values():
                                    for l in lekcje_dnia:
                                        if l["nauczyciel"] == kandydat["imie"] and l["godzina"] == godzina:
                                            zajety = True
                                            break
                                    if zajety:
                                        break
                                if zajety:
                                    break
                            if not zajety:
                                wolni.append(kandydat)

                        if wolni:
                            wybrany = random.choice(wolni)
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
    print(f"\n✅ Zapisano: {OUTPUT_PATH}")

    total = sum(len(zastepstwa[d]) for d in DNI)
    if total:
        stat = {"łączenie": 0, "zastępstwo": 0, "odwołane": 0}
        for dzien in DNI:
            for z in zastepstwa[dzien]:
                stat[z["status"]] += 1
        print(f"📊 Łącznie: {total} — łączeń: {stat['łączenie']}, zastępstw: {stat['zastępstwo']}, odwołanych: {stat['odwołane']}")
    else:
        print("ℹ️ Brak zastępstw — wszyscy obecni.")


if __name__ == "__main__":
    main()
