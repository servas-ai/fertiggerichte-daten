"""Merge fit2go.meals (fittogo.at) ready meals into other.json + ftg_items.json — idempotent
(replaces all 'Fit to Go online' rows). Source: newest evidence snapshot
fertiggerichte-daten/raw/fittogo_<stamp>.json from scripts/enrich_fittogo.py
(food-connectors `fittogo` adapter: public sitemap + product HTML). Snapshot so the
hourly export does not hit fittogo.at ~30 times. price_eur = published 12er-box 9,99 €/Meal."""
import json, glob, re, os
STORE = "Fit to Go online"
DATEN = "/workspace/fertiggerichte-daten/raw"
DAY = None

def latest():
    fs = sorted(glob.glob(f"{DATEN}/fittogo_20*.json")); return fs[-1] if fs else None

def rows(path=None):
    global DAY
    path = path or latest()
    if not path: return []
    d = json.load(open(path)); stamp = d["fetched"]; DAY = stamp[:10]; out = []
    for p in d["products"]:
        n = p["nutrition_100g"]; size = p["size_g"]; x = p["extra"]
        if x.get("image_head") != 200 or not size or n.get("protein") is None: continue
        pack = x.get("pack_nutrition") or {}
        pp = pack.get("protein") or round(n["protein"] * size / 100, 1)
        kp = pack.get("kcal") or (round(n["kcal"] * size / 100) if n.get("kcal") is not None else None)
        veg = x.get("veg")
        out.append({
            "name": p["name"], "brand": "fit2go.meals (Fit2go GmbH)", "store": STORE,
            "price_eur": p["price_eur"], "size_g": size,
            "price_per_kg": p.get("unit_price_eur") or round(p["price_eur"] / size * 1000, 2),
            "url": p["source_url"], "image_url": p["image_url"], "ean": None,
            "kcal_100": n.get("kcal"), "protein_100": n.get("protein"), "fat_100": n.get("fat"),
            "satfat_100": n.get("satfat"), "carbs_100": n.get("carbs"), "sugar_100": n.get("sugar"),
            "fiber_100": n.get("fiber"), "salt_100": n.get("salt"),
            "protein_pack": pp, "kcal_pack": kp,
            "eur_per_10g_protein": round(p["price_eur"] / pp * 10, 2) if pp else None,
            "nutriscore": None, "manufacturer": p.get("producer") or "Fit2go GmbH, Piccoloweg 4, 4055 Pucking (FN 615822x)",
            "producer_id": None, "origin": "Österreich (lt. Hersteller)", "bio": False, "veg": veg,
            "prep": x.get("prep") or "TK; 7–10 Min Mikrowelle/Pfanne oder 40–45 Min Heißluftofen (lt. fittogo.at)",
            "instantpot": None, "category": "Online Meal-Prep",
            "price_source": f"fittogo.at/collections/12er-box, abgerufen {DAY}: 10,49 €/Meal (6er), 9,99 € (12er), 9,49 € (18er); Einzel-SKU im Shop 0,00 €",
            "price_date": DAY,
            "nut_source": f"fittogo.at Produktseite Pack-Nährwerte → /100 g {DAY} ({p['source_url']})",
            "packaging": f"Gesamt-Einwaage {int(size)} g (Bio-Pap-Schale)", "online": True, "available": True,
            "storage": "Tiefkühl (TK)", "shelf_life": "TK, schockgefrostet, 12 Monate",
            "shipping_eur": 4.99, "portions": 1, "article_no": p["source_id"],
            "ingredients": x.get("ingredients"), "allergens": x.get("allergens"),
        })
    return out

def merge_other(path="other.json"):
    cur = json.load(open(path))
    cur = [r for r in cur if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

def write_ftg_items(path="ftg_items.json"):
    new = rows(); json.dump(new, open(path, "w"), ensure_ascii=False, indent=1); return len(new)

if __name__ == "__main__":
    print("ftg_items:", write_ftg_items())
    print("other.json Fit to Go online:", merge_other())
