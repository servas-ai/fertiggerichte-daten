"""Merge Löwenanteil (loewenanteil.com) Bio glass-jar ready meals into online_mealprep.json —
idempotent (replaces all 'Online: Löwenanteil' rows).
Source: newest evidence snapshot fertiggerichte-daten/raw/loewenanteil_<stamp>.json written by
scripts/enrich_loewenanteil.py (food-connectors `loewenanteil` adapter: public Shopify products.json
for price/SKU/availability/images + public product HTML for edible size, nutrition per 100 g, ingredients).
Snapshot instead of a live crawl so the hourly export does not hit loewenanteil.com ~20 times.
Only meals with published price, size, nutrition and a HEAD-200 image. No GTIN published → ean None.
AT delivery: homepage country selector lists 'Österreich (EUR €)'; shipping fee under robots-Disallow
/policies/shipping-policy → shipping_eur null (not invented)."""
import json, glob, re
STORE = "Online: Löwenanteil"
DATEN = "/workspace/fertiggerichte-daten/raw"

def latest():
    fs = sorted(glob.glob(f"{DATEN}/loewenanteil_20*.json")); return fs[-1] if fs else None

def rows(path=None):
    path = path or latest()
    if not path: return []
    d = json.load(open(path)); day = d["fetched"][:10]; out = []
    for p in d["products"]:
        n = p["nutrition_100g"]; size = p["size_g"]; x = p["extra"]
        if x.get("image_head") != 200 or not p["price_eur"] or not size or n.get("protein") is None: continue
        pp = round(n["protein"] * size / 100, 1)
        veg = "vegan" if x.get("vegan") else False
        out.append({"name": p["name"], "brand": "Löwenanteil", "store": STORE, "price_eur": p["price_eur"], "size_g": size,
            "price_per_kg": p["unit_price_eur"] or round(p["price_eur"] / size * 1000, 2), "url": p["source_url"], "image_url": p["image_url"], "ean": None,
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None else None,
            "eur_per_10g_protein": round(p["price_eur"] / pp * 10, 2) if pp else None,
            "nutriscore": None, "manufacturer": "Löwenanteil GmbH, Heiligengeiststraße 6–8, 26121 Oldenburg (DE), HRB 212808",
            "producer_id": None, "origin": None, "bio": True,
            "veg": veg, "prep": "Mikrowelle 2–3 Min. / Topf (lt. loewenanteil.com)", "instantpot": None,
            "category": "Online Meal-Prep", "price_source": f"loewenanteil.com/products.json Einzelpreis {day} (Abo/Bundle günstiger)", "price_date": day,
            "nut_source": f"loewenanteil.com Nährwerttabelle pro 100 g {day} ({p['source_url']})",
            "nut_flag": None, "packaging": "Glas", "online": True, "available": x.get("available"),
            "storage": "Ungekühlt (Glas, steril)", "shelf_life": "ungekühlt über 1 Jahr (lt. Produktseiten)",
            "shipping_eur": None, "portions": x.get("portions") or 2, "sku": p["source_id"]})
    return out

def merge(path="online_mealprep.json"):
    cur = [r for r in json.load(open(path)) if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

if __name__ == "__main__":
    print("loewenanteil rows:", merge())
