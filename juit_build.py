"""Merge Juit (juit.com) dishes into online_mealprep.json — idempotent (replaces all 'Online: Juit' rows).
Source: food-connectors `juit` adapter = public storefront content bundle cdn.juit.gmbh/content-de.json.
Only currently sellable dishes with published weight + protein. No prices (api.juitnow.com price lists need
login → price_eur None, never estimated). AT shipping 8,99 € Express Standard (Juit FAQ in the same bundle)."""
import sys, json, datetime, re
sys.path.insert(0, '/workspace/food-connectors')
from food_connectors.adapters.juit import Juit
STORE = "Online: Juit"

def rows():
    today = datetime.date.today().isoformat(); out = []
    for p in Juit().fetch():
        n = p.nutrition_100g or {}; size = p.size_g
        if not n.get("protein") or not size: continue
        pp = round(n["protein"] * size / 100, 1)
        tags = p.extra.get("tags") or []
        veg = True if any(t in ("Vegan", "Vegetarian", "Vegetarisch") for t in tags) else None
        out.append({"name": p.name, "brand": "Juit", "store": STORE, "price_eur": None, "size_g": size, "price_per_kg": None,
            "url": p.source_url, "image_url": p.image_url, "ean": p.ean,
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") else None, "eur_per_10g_protein": None,
            "nutriscore": None, "manufacturer": "Juit GmbH, Lutterstraße 14, 33617 Bielefeld (DE)", "producer_id": None, "origin": None,
            "bio": False, "veg": veg, "prep": "Mikrowelle/Ofen/Pfanne", "instantpot": None, "category": "Online Meal-Prep",
            "price_source": f"kein öffentlicher Einzelpreis (juit.com Preisliste nur eingeloggt) — Stand {today}", "price_date": None,
            "nut_source": f"cdn.juit.gmbh/content-de.json {today} ({p.source_url})", "packaging": None, "online": True,
            "available": p.extra.get("sellable"), "storage": "Tiefkühl (TK)", "shelf_life": "TK; 3 Tage Kühlschrank ungeöffnet (Juit FAQ)",
            "shipping_eur": 8.99, "portions": p.extra.get("portions"), "tags": tags})
    return out

def merge(path="online_mealprep.json"):
    cur = [r for r in json.load(open(path)) if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

if __name__ == "__main__":
    print("juit rows:", merge())
