"""Merge Goldblatt (goldblatt.at) High Protein Bio-Fertiggerichte im Glas into online_mealprep.json —
idempotent (replaces all 'Online: Goldblatt' rows).
Source: newest evidence snapshot fertiggerichte-daten/raw/goldblatt_<stamp>.json written by
scripts/enrich_goldblatt.py (food-connectors `goldblatt` adapter: public Shopify /products.json for
price/handle/availability/images + product HTML Nährwerttabelle pro 100 g / pro Glas, Zutaten, Zubereitung).
Snapshot instead of a live crawl so the hourly export does not hit goldblatt.at.
Only meals with published price, size, nutrition and a HEAD-200 image. No GTIN published.
AT shipping (goldblatt.at/policies/shipping-policy): 5,99 € ab 30 € (darunter 9,99 €), gratis ab 90 €, Post 1–3 Werktage.
Operator Golden Veggies GmbH, FN 550344f, UID ATU76525048 (VIES valid 2026-10-14)."""
import json, glob
STORE = "Online: Goldblatt"
DATEN = "/workspace/fertiggerichte-daten/raw"
MANU = "Golden Veggies GmbH, Wagerberg 37, 8271 Bad Waltersdorf, FN 550344f"

def latest():
    fs = sorted(glob.glob(f"{DATEN}/goldblatt_20*.json")); return fs[-1] if fs else None

def rows(path=None):
    path = path or latest()
    if not path: return []
    d = json.load(open(path)); day = d["fetched"][:10]; ship = (d.get("shipping_at") or {}).get("fee"); out = []; seen = set()
    for p in d["products"]:
        n = p["nutrition_100g"]; size = p["size_g"]; x = p["extra"]
        key = x.get("handle") or p["source_url"]
        if key in seen: continue
        if x.get("image_head") != 200 or not p["price_eur"] or not size or n.get("protein") is None: continue
        seen.add(key)
        pp = round(n["protein"] * size / 100, 1)
        out.append({"name": p["name"], "brand": "Goldblatt", "store": STORE, "price_eur": p["price_eur"], "size_g": size,
            "price_per_kg": p["unit_price_eur"] or round(p["price_eur"] / size * 1000, 2), "url": p["source_url"], "image_url": p["image_url"], "ean": p.get("ean"),
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None else None,
            "eur_per_10g_protein": round(p["price_eur"] / pp * 10, 2) if pp else None,
            "nutriscore": None, "manufacturer": MANU, "producer_id": None, "origin": "AT (Steiermark)", "bio": bool(x.get("bio")) or None,
            "veg": "vegan" if x.get("vegan") else False,
            "prep": "Topf kurz erhitzen oder Mikrowelle 2–3 Min. (lt. goldblatt.at)", "instantpot": None,
            "category": "Online Meal-Prep", "price_source": f"goldblatt.at/products.json Einzelpreis {day} (Pakete günstiger)", "price_date": day,
            "nut_source": f"goldblatt.at Nährwerttabelle pro 100 g {day} ({p['source_url']})",
            "nut_flag": None, "packaging": "Glas", "online": True, "available": x.get("available"),
            "storage": "Ungekühlt (Glas)", "shelf_life": "ungekühlt bis zu 3 Monate (lt. Produktseiten)",
            "shipping_eur": ship, "portions": x.get("portions"), "sku": p["source_id"]})
    return out

def merge(path="online_mealprep.json"):
    cur = [r for r in json.load(open(path)) if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

if __name__ == "__main__":
    print("goldblatt rows:", merge())
