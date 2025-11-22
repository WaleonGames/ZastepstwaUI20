#!/usr/bin/env python3
# 🧑‍🏫 Generator zastępstw v14.1 — generuje zastępstwa NA NASTĘPNY DZIEŃ
# Plik wynikowy: data/zastepstwa/YYYY-MM-DD.json

import json, os, re, datetime

DATA_DIR = "data"
PLANY_DIR = os.path.join(DATA_DIR, "plany")
ZAST_DIR = os.path.join(DATA_DIR, "zastepstwa")

# ============================================================
# DATA: JUTRO
# ============================================================

TODAY = datetime.date.today()
TOMORROW = TODAY + datetime.timedelta(days=1)
DATE_STR = TOMORROW.strftime("%Y-%m-%d")

# english → polish dni tygodnia
MAPA_DNI = {
    "monday": "poniedzialek",
    "tuesday": "wtorek",
    "wednesday": "sroda",
    "thursday": "czwartek",
    "friday": "piatek",
    "saturday": "sobota",
    "sunday": "niedziela"
}

DZIEN_ENG = TOMORROW.strftime("%A").lower()
DZIEN = MAPA_DNI[DZIEN_ENG]  # nazwa dnia PL

OUTPUT_PATH = os.path.join(ZAST_DIR, f"{DATE_STR}.json")


# ============================================================
# FUNKCJE
# ============================================================

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_rocznik(klasa):
    m = re.match(r"(\d+)", klasa)
    return int(m.group(1)) if m else None


# ============================================================
# GŁÓWNY PROGRAM — tylko na JUTRO
# ============================================================

def main():

    print(f"📅 Generuję zastępstwa na dzień: {DATE_STR} ({DZIEN})")

    nauczyciele = load_json(os.path.join(DATA_DIR, "nauczyciele.json"))
    if not isinstance(nauczyciele, list):
        nauczyciele = []

    klasy = [f[:-5] for f in os.listdir(PLANY_DIR) if f.endswith(".json")]
    plany = {
        k: load_json(os.path.join(PLANY_DIR, f"{k}.json"))
        for k in klasy
    }

    zastepstwa = []

    nieobecni = [n for n in nauczyciele if n.get("obecnosc") == "no"]
    obecni = [n for n in nauczyciele if n.get("obecnosc") == "yes"]

    print(f"🔍 Nieobecni nauczyciele: {len(nieobecni)}")

    # ------------------------------------------------------------
    # DLA KAŻDEGO NIEOBECNEGO
    # ------------------------------------------------------------
    for n in nieobecni:

        imie = n["imie"]
        print(f"\n🚫 {imie} — nieobecny")

        for klasa, plan in plany.items():

            lekcje_jutro = plan.get(DZIEN, [])

            for lekcja in lekcje_jutro:

                if lekcja.get("nauczyciel") != imie:
                    continue

                godzina = lekcja["godzina"]
                przedmiot = lekcja["przedmiot"]

                status = "odwołane"
                nauczyciel_zast = None
                opis = "Zajęcia odwołane"

                # =====================================================
                # 1) PRÓBA ŁĄCZENIA KLAS
                # =====================================================
                polaczone_z = None

                for inna_klasa, plan2 in plany.items():

                    if inna_klasa == klasa:
                        continue

                    lekcja2 = next(
                        (l2 for l2 in plan2.get(DZIEN, []) if l2.get("godzina") == godzina),
                        None
                    )
                    if not lekcja2:
                        continue

                    nauc2 = lekcja2.get("nauczyciel")
                    if not nauc2:
                        continue

                    nauc2_obj = next((x for x in nauczyciele if x["imie"] == nauc2), None)
                    if not nauc2_obj or nauc2_obj.get("obecnosc") == "no":
                        continue

                    # różnica poziomów max 1
                    r1 = extract_rocznik(klasa)
                    r2 = extract_rocznik(inna_klasa)
                    if r1 and r2 and abs(r1 - r2) > 1:
                        continue

                    polaczone_z = inna_klasa
                    nauczyciel_zast = nauc2
                    status = "łączenie"
                    opis = f"Połączono klasy {klasa} i {inna_klasa}"
                    break

                # =====================================================
                # 2) PRÓBA ZASTĘPSTWA
                # =====================================================
                if not polaczone_z:
                    wolni = []

                    for kandydat in obecni:

                        zajety = False
                        for p in plany.values():
                            for ld in p.get(DZIEN, []):
                                if ld.get("nauczyciel") == kandydat["imie"] and ld["godzina"] == godzina:
                                    zajety = True
                                    break
                            if zajety:
                                break

                        if not zajety:
                            wolni.append(kandydat)

                    if wolni:
                        wybrany = wolni[0]
                        nauczyciel_zast = wybrany["imie"]
                        status = "zastępstwo"
                        opis = f"Zastępuje {wybrany['imie']}"

                # =====================================================
                # ZAPIS
                # =====================================================
                zastepstwa.append({
                    "godzina": godzina,
                    "klasa": klasa,
                    "przedmiot": przedmiot,
                    "nauczyciel_nieobecny": imie,
                    "nauczyciel_zastepujacy": nauczyciel_zast,
                    "status": status,
                    "opis": opis
                })

    save_json(OUTPUT_PATH, zastepstwa)

    print(f"\n📊 Wygenerowano {len(zastepstwa)} pozycji.")
    print(f"📁 Plik zapisany: {OUTPUT_PATH}")


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
