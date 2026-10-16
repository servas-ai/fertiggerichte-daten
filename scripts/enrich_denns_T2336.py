"""denn's BioMarkt ready meals, Daten-Squad 2026-10-16T2336 (denn's 5 → 15 rows).
Sources (no login/cookies, food-connectors polite gate = robots.txt + 1 req/s/host):
  1. dennree brand catalog www.dennree.de (dennree = own brand of the dennree group, operator of denn's BioMarkt DE+AT),
     categories pizza / flammkuchen / veg-bratlinge--pfannengerichte via food-connectors `denns` (dennree_catalog):
     name, net weight, legal denomination, ingredients, nutrition per 100 g as published (Atwater-checked, all 9 pass),
     packshot images.dennree.de/fitinto/576x384/<denn's article no>.front.png (HTTP 200, 'BILD FOLGT' placeholder → no photo).
     No price, no GTIN on the brand site → none set. DE brand site: AT availability per article NOT stated (marked in source).
  2. denns-biomarkt.at 'Neu im Sortiment' page-data (isInAustria=true): followfood Piccoli Tomate & Mozzarella 270 g,
     regular shelf price 6,29 € (1 kg = 23,22 €), official Sanity packshot; no EAN / nutrition published → none set.
Writes data/{products,prices,nutrition}.{csv,json} (append, dedupe chain+name) + data/supplemental/* (so export.py keeps them)
and evidence raw/denns_2026-10-16T2336.json. Input: food-connectors live snapshot (EV env, default /tmp/denns_ev.json)."""
import csv, json, os, hashlib, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOT, TODAY = "2026-10-16T2336", "2026-10-16"; CHAIN = "Denn's"
ev = json.load(open(os.environ.get("EV", "/tmp/denns_ev.json")))
def pid(url, name): return hashlib.sha1((url + "|" + name + "|" + CHAIN).encode()).hexdigest()[:12]
NEW_MEALS = {"followfood Piccoli Tomate & Mozzarella"}  # only ready meals from 'Neu im Sortiment' (rest: biscuits, wine, kefir, flakes, desserts, tuna)
prods, prices, nuts, rejected = [], [], [], []
for p in ev["dennree_catalog"]:
    x = p["extra"]
    if x.get("atwater_ok") is not True: rejected.append({"name": p["name"], "reason": "Atwater check failed/incomplete"}); continue
    frozen = x.get("frozen"); veg = p["name"].lower().startswith("dennree vegane")
    i = pid(p["source_url"], p["name"])
    prods.append({"product_id": i, "name": p["name"], "brand": "dennree", "chain": CHAIN, "dish": None,
        "storage": "Tiefkühl (TK)" if frozen else ("Kühlregal (Menüschale/frisch)" if "Schutzatmosphäre" in (x.get("notes") or "") else "Unklar (keine Lagerangabe)"),
        "pack_size_g": float(p["size_g"]) if p["size_g"] else None, "producer": "dennree GmbH", "origin": None, "bio": True, "vegan": veg,
        "url": p["source_url"], "image_url": p["image_url"],
        "source": f"dennree.de Markenkatalog (denn's-Eigenmarke dennree, DE-Markenseite; AT-Verfügbarkeit je Artikel nicht angegeben; food-connectors denns eigenmarke, live {TODAY}, Artikel {p['source_id']})",
        "ean": None})
    n = p["nutrition_100g"]
    nuts.append({"product_id": i, "kcal_100g": n.get("kcal"), "protein_100g": n.get("protein"), "fat_100g": n.get("fat"),
        "saturated_fat_100g": n.get("satfat"), "carbs_100g": n.get("carbs"), "sugar_100g": n.get("sugar"), "fiber_100g": n.get("fiber"),
        "salt_100g": n.get("salt"), "nutri_score": None, "health_score": None, "eur_per_10g_protein": None})
for p in ev["neu_im_sortiment"]:
    if p["name"] not in NEW_MEALS: rejected.append({"name": p["name"], "reason": "Neu im Sortiment: kein Fertiggericht"}); continue
    x = p["extra"]; i = pid(p["source_url"], p["name"])
    prods.append({"product_id": i, "name": p["name"], "brand": p["brand"], "chain": CHAIN, "dish": None, "storage": "Unklar (keine Lagerangabe)",
        "pack_size_g": float(p["size_g"]), "producer": None, "origin": None, "bio": "EU-Bio-Siegel" in (x.get("labels") or []), "vegan": False,
        "url": p["source_url"], "image_url": p["image_url"],
        "source": f"denns-biomarkt.at Neu im Sortiment (AT, food-connectors denns neu, live {TODAY})", "ean": None})
    prices.append({"product_id": i, "chain": CHAIN, "price_eur": p["price_eur"], "price_per_kg_eur": p["unit_price_eur"], "price_status": "live 2026",
        "fetched_at": TODAY, "price_source": f"food-connectors/denns {TODAY} (denn's BioMarkt AT 'Neu im Sortiment' page-data, isInAustria): Regalpreis {p['price_eur']} €; {x.get('unit_price_text')}; Packung {x.get('pack')}"})
def load_csv(n): return list(csv.DictReader(open(f"{R}/data/{n}.csv")))
have = {(r["chain"], r["name"].strip().lower()) for r in load_csv("products")}
haveid = {r["product_id"] for r in load_csv("products")}
new = [r for r in prods if (r["chain"], r["name"].strip().lower()) not in have and r["product_id"] not in haveid]
keep = {r["product_id"] for r in new}
add = {"products": new, "prices": [r for r in prices if r["product_id"] in keep], "nutrition": [r for r in nuts if r["product_id"] in keep]}
if "--write" in sys.argv:
    for n, rows in add.items():
        if not rows: continue
        fields = list(load_csv(n)[0].keys())
        with open(f"{R}/data/{n}.csv", "a", newline="") as fh:
            w = csv.DictWriter(fh, fields, extrasaction="ignore")
            for r in rows: w.writerow(r)
        js = json.load(open(f"{R}/data/{n}.json")); js += rows
        json.dump(js, open(f"{R}/data/{n}.json", "w"), ensure_ascii=False, indent=1)
        sp = f"{R}/data/supplemental/{n}.json"; sj = json.load(open(sp)) if os.path.exists(sp) else []
        ids = {r["product_id"] for r in sj}; sj += [r for r in rows if r["product_id"] not in ids]
        json.dump(sj, open(sp, "w"), ensure_ascii=False, indent=1)
    out = dict(ev); out["rows_added"] = add; out["rejected"] = rejected
    out["excluded_categories"] = {"tuetensuppe": "dry soup mixes (8: Gemüse-, Hühner-, Kartoffelcreme-, Kürbiscreme-, Pilzcreme-, Spargelcreme-, Tomatencreme-, Zwiebelsuppe)",
                                  "tomatenprodukte/sugo": "sauces", "bruehen": "stock", "gemuesekonserven/weisse-bohnen-in-tomatensauce": "canned side, not a dish"}
    json.dump(out, open(f"{R}/raw/denns_{SLOT}.json", "w"), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in add.items()}, "rejected", len(rejected))
for r in new: print(" ", r["product_id"], r["name"], r["storage"], r["pack_size_g"], bool(r["image_url"]))
