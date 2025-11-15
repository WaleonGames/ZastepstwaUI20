#!/usr/bin/env python3
# 🧑‍🏫 Generator zastępstw v13 — zgodny z 3 zasadami:
# 1) Łączenie klas — tylko jeśli druga klasa ma lekcję i nauczyciel jest obecny
# 2) Zastępstwo — jeśli nie można połączyć
# 3) Odwołane — jeśli nie można połączyć i brak wolnych nauczycieli

import json, os, re

DATA_DIR = "data"
PLANY_DIR = os.path.join(DATA_DIR, "plany")
OUTPUT_PATH = os.path.join(DATA_DIR, "zastepstwa.json")

DNI = ["poniedzialek", "wtorek", "sroda", "czwartek", "piatek"]

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
# GŁÓWNY PROGRAM
# ============================================================

def main():

    nauczyciele = load_json(os.path.join(DATA_DIR, "nauczyciele.json"))
    if not isinstance(nauczyciele, list):
        nauczyciele = []

    # wszystkie plany klas
    klasy = [f[:-5] for f in os.listdir(PLANY_DIR) if f.endswith(".json")]
    plany = {
        k: load_json(os.path.join(PLANY_DIR, f"{k}.json"))
        for k in klasy
    }

    zastepstwa = {d: [] for d in DNI}

    nieobecni = [n for n in nauczyciele if n.get("obecnosc") == "no"]
    obecni = [n for n in nauczyciele if n.get("obecnosc") == "yes"]

    print(f"🔍 Nieobecni nauczyciele: {len(nieobecni)}")

    # ------------------------------------------------------------
    # DLA KAŻDEGO NIEOBECNEGO
    # ------------------------------------------------------------
    for n in nieobecni:

        imie = n["imie"]
        powod = n.get("powod", "brak informacji")

        print(f"\n🚫 {imie} — nieobecny")

        for klasa, plan in plany.items():

            for dzien, lekcje in plan.items():

                for lekcja in lekcje:

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

                        # znajdź lekcję o tej samej godzinie
                        lekcja2 = next(
                            (l2 for l2 in plan2.get(dzien, []) if l2.get("godzina") == godzina),
                            None
                        )

                        if not lekcja2:
                            continue  # okienko
                        if not lekcja2.get("przedmiot"):
                            continue
                        if not lekcja2.get("nauczyciel"):
                            continue

                        nauc2 = lekcja2["nauczyciel"]

                        # nauczyciel MUSI być obecny
                        nauc2_obj = next((x for x in nauczyciele if x["imie"] == nauc2), None)
                        if not nauc2_obj:
                            continue
                        if nauc2_obj.get("obecnosc") == "no":
                            continue

                        # różnica poziomów max 1
                        r1 = extract_rocznik(klasa)
                        r2 = extract_rocznik(inna_klasa)
                        if r1 is not None and r2 is not None:
                            if abs(r1 - r2) > 1:
                                continue

                        # Mamy łączenie
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

                            # sprawdzamy czy kandydat ma lekcję w tej godzinie
                            zajety = False
                            for p in plany.values():
                                for ld in p.get(dzien, []):
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
                    # 3) OSTATECZNIE: ODWOŁANE
                    # =====================================================

                    if not polaczone_z and not nauczyciel_zast:
                        status = "odwołane"
                        opis = "Zajęcia odwołane"

                    # =====================================================
                    # ZAPIS
                    # =====================================================

                    zastepstwa[dzien].append({
                        "godzina": godzina,
                        "klasa": klasa,
                        "przedmiot": przedmiot,
                        "nauczyciel_nieobecny": imie,
                        "nauczyciel_zastepujacy": nauczyciel_zast,
                        "status": status,
                        "opis": opis
                    })

    # ZAPIS
    save_json(OUTPUT_PATH, zastepstwa)

    total = sum(len(zastepstwa[d]) for d in DNI)
    print(f"\n📊 Wygenerowano łącznie: {total} pozycji zastępstw.")


# ============================================================
# START
# ============================================================
if __name__ == "__main__":
    main()
