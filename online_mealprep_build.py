import sys, json, re, datetime
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/workspace/food-connectors')
from food_connectors.adapters.mealprep import PrepMyMeal, LiveFresh
today = datetime.date.today().isoformat()
NONMEAL = re.compile(r"drink|shot|saft|riegel|bar\b|açaí|acai|müsli|porridge|pancake|shake|pulver|snack|dessert|pudding|cookie|brownie|kids|ballaststoff", re.I)
rows = []
for A in (PrepMyMeal(), LiveFresh()):
    ps = [p for p in A.fetch() if not NONMEAL.search(p.name)]
    with ThreadPoolExecutor(8) as ex: ps = list(ex.map(A.enrich, ps))
    for p in ps:
        n = p.nutrition_100g or {}
        size = p.size_g
        if size is None:
            m = re.search(r"\((?:XL, )?2 Portionen\)", p.name)
        if not n.get("protein") or not size: continue  # never invent: skip items without published nutrition / weight
        pp = round(n["protein"] * size / 100, 1)
        rows.append({"name": p.name, "brand": p.brand, "store": p.store, "price_eur": p.price_eur, "size_g": size,
            "price_per_kg": round(p.price_eur / size * 1000, 2) if p.price_eur else None, "url": p.source_url, "image_url": p.image_url,
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") else None,
            "eur_per_10g_protein": round(p.price_eur / pp * 10, 2) if p.price_eur and pp else None,
            "nutriscore": None, "manufacturer": None, "producer_id": None, "origin": None, "bio": False, "veg": None,
            "prep": "Mikrowelle/Pfanne", "instantpot": None, "category": "Online Meal-Prep",
            "price_source": f"{A.domain}/products.json {today}", "price_date": today, "nut_source": p.source_url,
            "packaging": None, "online": True, "available": p.extra.get("available")})
for x in rows: x["storage"]="Tiefkühl (TK)"; x["shelf_life"]="≥3 Monate TK / 3–4 Tage gekühlt" if "Prep" in x["store"] else "TK (−18 °C)"; x["shipping_eur"]=5.99 if "Prep" in x["store"] else 9.95
json.dump(rows, open('online_mealprep.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter; print(len(rows), Counter(r['store'] for r in rows))
import juit_build; print("juit", juit_build.merge())  # Juit (juit.com) dishes, idempotent
import bofrost_build; print("bofrost", bofrost_build.merge())  # bofrost* Austria ready meals from the newest daten snapshot, idempotent
