"""Merge every. (every-foods.com) frozen ready meals into online_mealprep.json — idempotent (replaces all 'Online: every.' rows).
Source: newest evidence snapshot fertiggerichte-daten/raw/every_<stamp>.json written by scripts/enrich_every.py
(food-connectors `every` adapter: public Shopify storefront JSON eat.every-foods.com/products.json for price/SKU/availability/
images + public product pages every-foods.com/products/<handle> for weight, nutrition per 100 g, ingredients, preparation).
Snapshot instead of a live crawl so the hourly export does not hit every-foods.com ~55 times.
Only meals with published price, weight, nutrition and a HEAD-200 image. No GTIN published → ean None.
AT delivery: shop's own shipping policy (eat.every-foods.com/policies/shipping-policy) lists 'Österreich (DPD)';
regular shipping 5,99 €, free from 8 meals (AGB §6 still says Germany only — conflict kept in the evidence file)."""
import json, glob, re
STORE = "Online: every."
DATEN = "/workspace/fertiggerichte-daten/raw"
MEAT_ING = re.compile(r"fleisch|huhn|hühn|hähnchen|pute|rind|schwein|kalb|lamm|speck|schinken|salami|wurst|leber|geflügel|fisch|lachs|"
                      r"thunfisch|garnele|gelatine|schmalz|\bei\b|eier|vollei|milch(?!säure)|butter(?!milch)|sahne|käse|joghurt|honig", re.I)

def latest():
    fs = sorted(glob.glob(f"{DATEN}/every_20*.json")); return fs[-1] if fs else None

def rows(path=None):
    path = path or latest()
    if not path: return []
    d = json.load(open(path)); day = d["fetched"][:10]; out = []
    for p in d["products"]:
        n = p["nutrition_100g"]; size = p["size_g"]; x = p["extra"]
        if x.get("image_head") != 200 or not p["price_eur"] or not size or n.get("protein") is None: continue
        pp = round(n["protein"] * size / 100, 1)
        ing = re.split(r"(?:^|[.\n])\s*Kann\s", x.get("ingredients") or "")[0]  # 'Kann … enthalten' trace notes are not ingredients
        # every. labels its range plant-based; veg from the shop's 'Vegan' tag, else from the ingredient list, else None
        veg = True if x.get("vegan") else ((False if MEAT_ING.search(ing) else True) if ing else None)
        out.append({"name": p["name"], "brand": "every.", "store": STORE, "price_eur": p["price_eur"], "size_g": size,
            "price_per_kg": p["unit_price_eur"] or round(p["price_eur"] / size * 1000, 2), "url": p["source_url"], "image_url": p["image_url"], "ean": None,
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None else None,
            "eur_per_10g_protein": round(p["price_eur"] / pp * 10, 2) if pp else None,
            "nutriscore": None, "manufacturer": "Every. GmbH, Ritterstraße 9–10, 10969 Berlin (DE), HRB 221768 B",
            "producer_id": None, "origin": None, "bio": None,  # Bio-Kontrollstelle DE-ÖKO-001 im Impressum, aber Bio-Status je Gericht nicht veröffentlicht
            "veg": veg, "prep": "Pfanne/Mikrowelle (lt. every-foods.com)", "instantpot": None,
            "category": "Online Meal-Prep", "price_source": f"eat.every-foods.com/products.json Einzelpreis {day} (Bundles/Abo günstiger)", "price_date": day,
            "nut_source": f"every-foods.com Nährwerttabelle pro {x.get('nutrition_per') or '100 g'} {day} ({p['source_url']})",
            "nut_flag": ("Packungsspalte inkonsistent: " + ",".join(x["pack_inconsistent"]) + " (pro 100 g verwendet)") if x.get("pack_inconsistent") else None,
            "packaging": None, "online": True, "available": x.get("available"),
            "storage": "Tiefkühl (TK)", "shelf_life": "bis 12 Monate TK ab Produktion; aufgetaut binnen 24 h (every FAQ)",
            "shipping_eur": 5.99, "portions": 1, "sku": p["source_id"], "every_subtype": p["category"]})
    return out

def merge(path="online_mealprep.json"):
    cur = [r for r in json.load(open(path)) if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

if __name__ == "__main__":
    print("every rows:", merge())
