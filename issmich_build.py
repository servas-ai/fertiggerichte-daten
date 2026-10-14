"""Merge iss mich! (issmich.at) Wiener Bio-Eintöpfe & Suppen im WECK-Pfandglas into online_mealprep.json —
idempotent (replaces all 'Online: iss mich!' rows).
Source: newest evidence snapshot fertiggerichte-daten/raw/issmich_<stamp>.json written by scripts/enrich_issmich.py
(food-connectors `issmich` adapter: Shopware 6 product pages with schema.org microdata — price, Streichpreis, Pfand,
Inhalt, GTIN-13, availability, packshots, Zutaten; Nährwerte = vision-verified transcription of the official
Nährwerttabelle image, independently confirmed by strict OCR for most items).
Snapshot instead of a live crawl so the hourly export does not hit issmich.at.
Only Eintöpfe/Suppen with published price, size, nutrition and a HEAD-200 image (Beilagen/Süßes/Saucen excluded).
AT shipping (issmich.at/versand-und-bezahlung): nur Österreich, 9,90 €, frei ab 99 €; +2,00 € Pfand je WECK-Glas.
Operator iss mich! GmbH, FN 471722i (HG Wien), UID ATU72305301 (VIES valid 2026-10-14)."""
import json, glob
STORE = "Online: iss mich!"
DATEN = "/workspace/fertiggerichte-daten/raw"
MANU = "iss mich! GmbH, Erlafstraße 7, 1020 Wien, FN 471722i"
MEALS = ("Eintopf", "Suppe")

def latest():
    fs = sorted(glob.glob(f"{DATEN}/issmich_20*.json")); return fs[-1] if fs else None

def rows(path=None):
    path = path or latest()
    if not path: return []
    d = json.load(open(path)); day = d["fetched"][:10]; ship = (d.get("shipping_at") or {}).get("fee"); out = []; seen = set()
    for p in d["products"]:
        n = p["nutrition_100g"]; size = p["size_g"]; x = p["extra"]
        key = p.get("source_id") or p["source_url"]
        if key in seen or x.get("course") not in MEALS: continue
        if x.get("image_head") != 200 or not p["price_eur"] or not size or n.get("protein") is None: continue
        seen.add(key)
        pp = round(n["protein"] * size / 100, 1)
        veg = "vegan" if x.get("vegan") else (True if x.get("vegetarian") else False)  # True = vegetarisch (bofrost/Juit convention)
        lp = x.get("list_price_eur")
        out.append({"name": p["name"], "brand": "iss mich!", "store": STORE, "price_eur": p["price_eur"], "size_g": size,
            "price_per_kg": p["unit_price_eur"] or round(p["price_eur"] / size * 1000, 2), "url": p["source_url"], "image_url": p["image_url"], "ean": p.get("ean"),
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None else None,
            "eur_per_10g_protein": round(p["price_eur"] / pp * 10, 2) if pp else None,
            "nutriscore": None, "manufacturer": MANU, "producer_id": None, "origin": "AT (Wien)", "bio": True,
            "veg": veg, "prep": "im Topf auf dem Herd erhitzen oder Mikrowelle 2–3 Min. (Einkochring entfernen, Deckel auflegen) lt. issmich.at", "instantpot": None,
            "category": "Online Meal-Prep",
            "price_source": f"issmich.at Produktseite {day}" + (f" (Aktion, Streichpreis {lp:.2f} €)".replace(".", ",") if lp else "") + " zzgl. 2,00 € Glas-Pfand",
            "price_date": day,
            "nut_source": f"issmich.at Nährwerttabelle (Bild) pro 100 g {day}, vision-verifiziert ({p['source_url']})",
            "nut_flag": x.get("nut_flag"), "packaging": "Glas", "online": True, "available": x.get("available"),
            "storage": None, "shelf_life": None,  # Lagerhinweis/MHD nicht veröffentlicht → nicht erfunden
            "shipping_eur": ship, "portions": 1, "sku": p["source_id"]})
    return out

def merge(path="online_mealprep.json"):
    cur = [r for r in json.load(open(path)) if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

if __name__ == "__main__":
    print("issmich rows:", merge())
