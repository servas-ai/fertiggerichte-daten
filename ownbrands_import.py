"""Convert ownbrands/{billa,spar,penny}_meals.json -> ownbrands_meals.json (score.py input). Dedupe vs existing app rows by store+name."""
import json, re
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower())
app = json.load(open("/workspace/fertig-app/public/data.json"))["rows"]
have = {(r.get("store", "").lower(), norm(r["name"])) for r in app}
STORE = {"billa": "BILLA", "spar": "SPAR", "penny": "PENNY"}
out, skipped = [], 0
for ch in ("billa", "spar", "penny"):
    for r in json.load(open(f"ownbrands/{ch}_meals.json")):
        if (ch, norm(r["name"])) in have: skipped += 1; continue
        n = r.get("nutrition_100g") or {}
        u = (r.get("unit") or "").lower(); sz = r.get("size")
        size_g = float(sz) if sz and u in ("g", "ml") else (float(sz) * 1000 if sz and u in ("kg", "l") else None)
        if size_g is None and r.get("price_eur") and r.get("price_per_kg_eur"): size_g = round(r["price_eur"] / r["price_per_kg_eur"] * 1000)
        g = lambda k: n.get(k)
        out.append({"name": r["name"], "brand": r.get("brand"), "store": STORE[ch], "price_eur": r.get("price_eur"), "size_g": size_g,
            "price_per_kg": r.get("price_per_kg_eur"), "price_date": r.get("price_date"), "price_source": r.get("source"),
            "url": r.get("url"), "image_url": r.get("image_url"), "ingredients": r.get("ingredients"),
            "kcal_100": g("kcal"), "protein_100": g("protein"), "fat_100": g("fat"), "satfat_100": g("satfat"), "carbs_100": g("carbs"),
            "sugar_100": g("sugar"), "fiber_100": g("fiber"), "salt_100": g("salt"),
            "protein_pack": round(g("protein") * size_g / 100, 1) if g("protein") is not None and size_g else None,
            "kcal_pack": round(g("kcal") * size_g / 100, 1) if g("kcal") is not None and size_g else None,
            "nutriscore": r.get("nutriscore"), "nutriscore_computed": r.get("nutriscore_computed"), "nova": r.get("nova"), "bio": r.get("bio"),
            "category": r.get("meal_type") or r.get("category"), "segment": "ready_meal", "availability_level": "chain", "ownbrand": True})
json.dump(out, open("ownbrands_meals.json", "w"), ensure_ascii=False, indent=0)
print("import", len(out), "skipped_dupes", skipped)
