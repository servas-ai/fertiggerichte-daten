"""Alfies (alfies.at) — Viennese online supermarket → ready-meal rows for chain 'Alfies' (Daten-Squad 2026-10-14T0740).

Source: food-connectors `alfies` adapter — listing via the public search-only Algolia index the alfies.at front-end
queries for every anonymous visitor (products_<warehouse>_de_at; category paths `ready-to-eat` = "Fix & Fertig" and
`frozen-ready-meals` = "Tiefgekühlte Fertiggerichte"), detail via the shop's public catalogue API
api.alfies.at/api/v1/catalogue/products-mm/<id> (nutrition text pro 100 g, ingredients, cross-retailer ids).
www.alfies.at robots.txt: `User-agent: * / Disallow:` (all allowed); api host has no robots.txt. No login/cookies,
detail calls 1 req/s. Warehouses resolved by the shop's own POST /api/get-warehouse: Wien = altha/guthe/macu,
Graz = graz, Linz = none (no delivery). Price = altha (Wien) display price incl. MwSt.
Kept rows: public, ready-meal category (minus doughs/baking mixes, potato/pickled salads, desserts, meat snacks), price,
kcal + protein per 100 g passing the Atwater plausibility gate (±25 % +15 kcal, macros ≤ 100 g) and in stock in at
least one AT warehouse at fetch time. Everything else stays in the raw evidence with its reason.
No GTIN on alfies.at → ean only twin-filled from an existing dataset row that Alfies itself links via billaId /
gurkerlId AND whose brand + pack size match (ean_source recorded in raw); otherwise empty.

Usage: python3 scripts/enrich_alfies.py raw/alfies_<stamp>.json   (idempotent: replaces previous Alfies rows in
data/supplemental/* and appends them to data/{products,prices,nutrition}.{csv,json} exactly like export.py does)."""
import sys, json, csv, re, hashlib, statistics, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN = "Alfies"
raw = json.load(open(sys.argv[1]))
STAMP = raw["fetched"][:10]

def pid(url, name): return hashlib.sha1(((url or "") + "|" + name + "|" + CHAIN).encode()).hexdigest()[:12]
def k(s): return re.sub(r"[^a-z0-9]", "", (s or "").lower())

prods_csv = list(csv.DictReader(open(f"{R}/data/products.csv")))
import collections
_bc = collections.Counter(r["brand"] for r in prods_csv if r["brand"] and r["chain"] != CHAIN)
brands = {}
for b, _ in _bc.most_common():  # most frequent spelling wins (Iglo, not iglo/IGLO)
    brands.setdefault(k(b), b)
billa = {}; gurk = {}
for r in prods_csv:
    u = r["url"] or ""
    m = re.search(r"billa\.at/produkte/.*-(\d{8})$", u)
    if m: billa[m.group(1)] = r
    m = re.search(r"gurkerl\.at/(\d+)", u)
    if m: gurk[m.group(1)] = r

def billa_key(b):
    m = re.fullmatch(r"(\d{2})-?(\d+)", (b or "").strip())
    return m.group(1) + m.group(2).zfill(6) if m else None

def storage(p):
    cats = set(p["extra"].get("category_slugs") or [])
    if p["extra"].get("frozen"): return "Tiefkühl (TK)"
    if "ready-made-canned-foods" in cats or re.search(r"\bDose\b", p["extra"].get("display_unit") or ""): return "Dose/Konserve"
    if "soups-instant-noodles" in cats and re.search(r"instant|cup|snack pot|quick snack|kaiser teller|bitte zu tisch|spaghetteria", p["name"], re.I): return "Trocken/Instant"
    if "fresh-ready-meals" in cats or "fresh-filled-pasta" in cats: return "Kühlregal (Menüschale/frisch)"
    return "Unklar (keine Lagerangabe)"

P, PR, N, used_ean = [], [], [], {}
for p in raw["kept"]:
    brand = brands.get(k(p["brand"]), p["brand"]) if p["brand"] else None
    ean, ean_src = None, None
    for kind, key, table in (("billa", billa_key(p["extra"].get("billa_id")), billa), ("gurkerl", str(p["extra"].get("gurkerl_id") or ""), gurk)):
        t = table.get(key) if key else None
        if t and t["ean"] and brand and k(t["brand"]) == k(brand) and t["pack_size_g"] and p["size_g"] and abs(float(t["pack_size_g"]) - p["size_g"]) < 1:
            ean, ean_src = t["ean"], f"twin {kind}:{key} ({t['chain']} '{t['name']}')"; break
    if ean and ean in used_ean: ean, ean_src = None, None  # never assign one GTIN to two Alfies rows
    if ean: used_ean[ean] = p["source_id"]
    p["extra"]["ean_twin"] = ean_src
    i = pid(p["source_url"], p["name"])
    n = p["nutrition_100g"]
    P.append({"product_id": i, "name": p["name"], "brand": brand, "chain": CHAIN, "dish": "", "storage": storage(p),
              "pack_size_g": p["size_g"], "producer": "", "origin": p.get("origin") or "",
              "bio": bool(re.search(r"\bbio\b", p["name"], re.I)), "vegan": bool(re.search(r"\bvegan\b", p["name"], re.I)),
              "url": p["source_url"], "image_url": p["image_url"], "source": f"alfies (food-connectors, live {STAMP})", "ean": ean})
    PR.append({"product_id": i, "chain": CHAIN, "price_eur": p["price_eur"],
               "price_per_kg_eur": round(p["price_eur"] / p["size_g"] * 1000, 2) if p["size_g"] else p.get("unit_price_eur"),
               "price_status": "live 2026", "fetched_at": STAMP,
               "price_source": f"alfies.at Wien (Warehouse altha) Algolia-Index {STAMP} (food-connectors alfies)"})
    ppe = round(p["price_eur"] / (n["protein"] * p["size_g"] / 100) * 10, 2) if p["size_g"] and n.get("protein") else ""
    N.append({"product_id": i, "kcal_100g": n.get("kcal"), "protein_100g": n.get("protein"), "fat_100g": n.get("fat"),
              "saturated_fat_100g": n.get("satfat"), "carbs_100g": n.get("carbs"), "sugar_100g": n.get("sugar"),
              "fiber_100g": n.get("fiber"), "salt_100g": n.get("salt"), "nutri_score": "", "health_score": "", "eur_per_10g_protein": ppe})
json.dump(raw, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)  # persist ean_twin evidence

ids = {x["product_id"] for x in P}
assert len(ids) == len(P), "duplicate product_id"
# 1) supplemental (re-appended by export.py on every refresh)
sup = f"{R}/data/supplemental"
for nm, rows in (("products", P), ("prices", PR), ("nutrition", N)):
    cur = json.load(open(f"{sup}/{nm}.json"))
    old_ids = {x["product_id"] for x in json.load(open(f"{sup}/products.json")) if x.get("chain") == CHAIN}
    cur = [x for x in cur if x["product_id"] not in old_ids and x.get("chain") != CHAIN]
    json.dump(cur + rows, open(f"{sup}/{nm}.json", "w"), ensure_ascii=False, indent=1)
# 2) published tables (same columns/serialisation as export.write)
for nm, rows in (("products", P), ("prices", PR), ("nutrition", N)):
    js = json.load(open(f"{R}/data/{nm}.json"))
    prev = {x["product_id"] for x in json.load(open(f"{R}/data/products.json")) if x.get("chain") == CHAIN}
    js = [x for x in js if x["product_id"] not in prev and x["product_id"] not in ids]
    js += rows
    json.dump(js, open(f"{R}/data/{nm}.json", "w"), ensure_ascii=False, indent=1)
    fields = list(csv.DictReader(open(f"{R}/data/{nm}.csv")).fieldnames)
    with open(f"{R}/data/{nm}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore"); w.writeheader()
        for r in js: w.writerow({kk: ("|".join(map(str, v)) if isinstance(v, list) else v) for kk, v in r.items()})
print(f"Alfies rows: {len(P)} products / {len(PR)} prices / {len(N)} nutrition; EAN twin-filled {sum(1 for x in P if x['ean'])}; "
      f"median price {statistics.median(x['price_eur'] for x in PR)} €")
