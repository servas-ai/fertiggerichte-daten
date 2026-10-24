"""Build alfies_src.json (app staging rows) from fertiggerichte-daten Alfies rows + raw evidence (Daten-Squad).
Usage: python3 alfies_build.py /workspace/fertiggerichte-daten/raw/alfies_<stamp>.json
Keeps added_slot of rows already staged; new rows get the raw run stamp."""
import sys, json, csv, os
D = "/workspace/fertiggerichte-daten"
raw = json.load(open(sys.argv[1]))
slot_new = raw["fetched"]
old = {r["url"]: r for r in json.load(open("alfies_src.json"))} if os.path.exists("alfies_src.json") else {}
P = {r["product_id"]: r for r in csv.DictReader(open(f"{D}/data/products.csv")) if r["chain"] == "Alfies"}
PR = {r["product_id"]: r for r in csv.DictReader(open(f"{D}/data/prices.csv")) if r["product_id"] in P}
N = {r["product_id"]: r for r in csv.DictReader(open(f"{D}/data/nutrition.csv")) if r["product_id"] in P}
byurl = {p["source_url"]: p for p in raw["kept"]}
f = lambda v: float(v) if v not in ("", None) else None
out = []
for i, p in P.items():
    k = byurl[p["url"]]; n = N[i]; pr = PR[i]; size = f(p["pack_size_g"])
    nut = {x: f(n[f"{y}_100g"]) for x, y in (("kcal", "kcal"), ("protein", "protein"), ("fat", "fat"), ("satfat", "saturated_fat"),
                                               ("carbs", "carbs"), ("sugar", "sugar"), ("fiber", "fiber"), ("salt", "salt"))}
    date = pr["fetched_at"]
    pk = None if p["storage"].startswith("Unklar") else p["storage"]
    out.append({"name": p["name"], "brand": p["brand"] or None, "store": "Alfies", "price_eur": f(pr["price_eur"]), "size_g": size,
                "price_per_kg": f(pr["price_per_kg_eur"]), "url": p["url"], "image_url": p["image_url"],
                **{f"{x}_100": v for x, v in nut.items()},
                "protein_pack": round(nut["protein"] * size / 100, 1) if size and nut["protein"] is not None else None,
                "kcal_pack": round(nut["kcal"] * size / 100) if size and nut["kcal"] is not None else None,
                "manufacturer": None, "producer_id": None, "origin": None, "category": k.get("category"),
                "price_source": f"food-connectors/alfies {date} (alfies.at Wien warehouse altha, Algolia index price incl. MwSt.)",
                "price_date": date,
                "nut_source": f"Alfies catalogue API Nährwerttabelle je 100 {k['extra'].get('nutrition_basis') or 'g'} {date}",
                "ean": p["ean"] or None, "packaging": pk, "packaging_hint": pk, "is_meal": True,
                "delivery": "Alfies Lieferung Wien (60/120 Min) + Graz (Vorbestellung) – nicht Linz",
                "added_slot": (old.get(p["url"]) or {}).get("added_slot") or slot_new,
                "ingredients": k["extra"].get("ingredients")})
json.dump(out, open("alfies_src.json", "w"), ensure_ascii=False, indent=1)
print(len(out), "rows;", sum(1 for r in out if r["added_slot"] == slot_new), "new in", slot_new)
