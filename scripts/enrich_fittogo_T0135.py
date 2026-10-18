"""Daten-Squad 2026-10-18T0135: fit2go.meals catalogue grew 30 -> 32 meals on fittogo.at.

Source: food-connectors `fittogo` adapter (public product sitemap + product HTML, robots-allowed, no login).
The 2 handles new in the sitemap (cheesy-taco-bowl, topfennockerl-mit-erdbeersauce) are appended
idempotently to data/{products,prices,nutrition}.{json,csv} and data/supplemental/* (so a later
export.py refresh keeps them until the app build has them). Packshot = hero image of the product page
(adapter fix: the old png fallback picked the cross-sell grid photo of another meal); both photos
vision-checked (dish matches name). Price = published 12er-box meal price 9,99 EUR (single SKU 0,00 EUR).
Nutrition/100 g = pack values / Gesamt-Einwaage as printed. No EAN published.
Usage: python3 scripts/enrich_fittogo_T0135.py /tmp/fittogo_live_T0135.json"""
import sys, json, csv, hashlib, os
NEW = {"cheesy-taco-bowl", "topfennockerl-mit-erdbeersauce"}
CHAIN = "Fit to Go"
FETCHED = "2026-10-18"
PRICE_SRC = ("fittogo.at/collections/12er-box, abgerufen 2026-10-18: 10,49 €/Meal (6er), 9,99 € (12er), "
             "9,49 € (18er); Einzel-SKU im Shop 0,00 €")

def pid(url, name, store): return hashlib.sha1((url + "|" + name + "|" + store).encode()).hexdigest()[:12]

def rows(live):
    P, PR, N = [], [], []
    for x in live:
        if x["source_id"] not in NEW: continue
        i = pid(x["source_url"], x["name"], CHAIN)
        P.append({"product_id": i, "name": x["name"], "brand": "fit2go.meals (Fit2go GmbH)", "chain": CHAIN, "dish": None,
                  "storage": "Tiefkühl (TK)", "pack_size_g": x["size_g"], "producer": x["producer"],
                  "origin": "Österreich (lt. Hersteller)", "bio": False, "vegan": False, "url": x["source_url"],
                  "image_url": x["image_url"], "source": f"food-connectors/fittogo {FETCHED}: fittogo.at product page (hero packshot, pack nutrition, Gesamt-Einwaage)",
                  "ean": None})
        PR.append({"product_id": i, "chain": CHAIN, "price_eur": x["price_eur"], "price_per_kg_eur": x["unit_price_eur"],
                   "price_status": "live 2026", "fetched_at": FETCHED, "price_source": PRICE_SRC})
        n = x["nutrition_100g"]
        N.append({"product_id": i, "kcal_100g": n.get("kcal"), "protein_100g": n.get("protein"), "fat_100g": n.get("fat"),
                  "saturated_fat_100g": None, "carbs_100g": n.get("carbs"), "sugar_100g": None, "fiber_100g": None,
                  "salt_100g": None, "nutri_score": None, "health_score": None, "eur_per_10g_protein": None})
    return P, PR, N

def append(path_json, path_csv, new):
    if path_json:
        d = json.load(open(path_json)); have = {r["product_id"] for r in d}
        add = [r for r in new if r["product_id"] not in have]; d += add
        json.dump(d, open(path_json, "w"), ensure_ascii=False, indent=1)
    if path_csv:
        have = {r["product_id"] for r in csv.DictReader(open(path_csv))}
        hdr = next(csv.reader(open(path_csv)))
        with open(path_csv, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=hdr, extrasaction="ignore")
            for r in new:
                if r["product_id"] not in have:
                    w.writerow({k: ("" if v is None else v) for k, v in r.items()})
    return len(new)

def main(live_path):
    live = json.load(open(live_path))
    P, PR, N = rows(live)
    assert len(P) == len(NEW), P
    for nm, new in (("products", P), ("prices", PR), ("nutrition", N)):
        append(f"data/{nm}.json", f"data/{nm}.csv", new)
        append(f"data/supplemental/{nm}.json", None, new)
    ev = {"run": "Daten-Squad 2026-10-18T0135", "source": "food-connectors fittogo adapter (fittogo.at sitemap + product pages)",
          "sitemap_meals": len(live), "indexed_before": 30, "added": P, "prices": PR, "nutrition": N,
          "vision_gate": {"cheesy-taco-bowl": "PASS rice + kidney beans/corn/peppers + cheese sauce bowl",
                          "topfennockerl-mit-erdbeersauce": "PASS Topfennockerl on strawberry sauce with crumbs"},
          "adapter_fix": "hero <img> in the --photo frame preferred; old png fallback returned the cross-sell grid photo (30.png = Thai Red Curry) for both new pages; all 30 existing rows re-checked live: image unchanged",
          "dead_end": "shopbio.at Fertiggerichte (epages, robots OK): 6 Bio-Gläser je 6er-Karton 59,90 € (19,97 €/kg) — all 'Nicht auf Lager' on 2026-10-18, no nutrition, no producer named → not added"}
    json.dump(ev, open("raw/fittogo_2026-10-18T0135.json", "w"), ensure_ascii=False, indent=1)
    print("added", [p["name"] for p in P])

if __name__ == "__main__":
    main(sys.argv[1])
