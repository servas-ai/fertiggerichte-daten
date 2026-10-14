"""Merge Kernbeißer (kernbeisser.at) vegan Vollkorn-Fertiggerichte im Glas into online_mealprep.json —
idempotent (replaces all 'Online: Kernbeißer' rows).
Source: newest evidence snapshot fertiggerichte-daten/raw/kernbeisser_<stamp>.json written by
scripts/enrich_kernbeisser.py (food-connectors `kernbeisser` adapter: public WooCommerce Store API for
price/SKU/stock/images/description with Nährwerte pro 100 g + Zutaten + 450 g jar, product JSON-LD GTIN).
Snapshot instead of a live crawl so the hourly export does not hit kernbeisser.at.
Only meals with published price, size, nutrition and a HEAD-200 image. AT-only delivery, free shipping,
minimum order 6 glasses (site header)."""
import json, glob
STORE = "Online: Kernbeißer"
DATEN = "/workspace/fertiggerichte-daten/raw"
MANU = "Kernbeißer OG, Jheringgasse 33/2/8, 1150 Wien, FN 622470y"

def latest():
    fs = sorted(glob.glob(f"{DATEN}/kernbeisser_20*.json")); return fs[-1] if fs else None

def rows(path=None):
    path = path or latest()
    if not path: return []
    d = json.load(open(path)); day = d["fetched"][:10]; out = []
    for p in d["products"]:
        n = p["nutrition_100g"]; size = p["size_g"]; x = p["extra"]
        if x.get("image_head") != 200 or not p["price_eur"] or not size or n.get("protein") is None: continue
        pp = round(n["protein"] * size / 100, 1)
        out.append({"name": p["name"], "brand": "Kernbeißer", "store": STORE, "price_eur": p["price_eur"], "size_g": size,
            "price_per_kg": p["unit_price_eur"] or round(p["price_eur"] / size * 1000, 2), "url": p["source_url"], "image_url": p["image_url"], "ean": p.get("ean"),
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None else None,
            "eur_per_10g_protein": round(p["price_eur"] / pp * 10, 2) if pp else None,
            "nutriscore": None, "manufacturer": MANU, "producer_id": None, "origin": "AT (Wien)", "bio": None,
            "veg": "vegan" if x.get("vegan") else False,
            "prep": "Topf/Pfanne kurz erwärmen oder Mikrowelle ca. 3 Min. (lt. kernbeisser.at)", "instantpot": None,
            "category": "Online Meal-Prep", "price_source": f"kernbeisser.at WooCommerce Store API Einzelpreis je Glas {day} (Mindestbestellung 6 Gläser)", "price_date": day,
            "nut_source": f"kernbeisser.at Nährwerte pro 100 g {day} ({p['source_url']})",
            "nut_flag": None, "packaging": "Glas", "online": True, "available": x.get("in_stock"),
            "storage": "Ungekühlt (Glas)", "shelf_life": None,
            "shipping_eur": 0.0, "portions": None, "sku": p["source_id"]})
    return out

def merge(path="online_mealprep.json"):
    cur = [r for r in json.load(open(path)) if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

if __name__ == "__main__":
    print("kernbeisser rows:", merge())
