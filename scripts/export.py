"""Export the app's verified data into open CSV + JSON tables. Safe for the hourly run:
FERTIG_SRC=/workspace/fertig FERTIG_APP=/workspace/fertig-app/public python3 scripts/export.py && python3 scripts/validate.py"""
import json, csv, os, re, hashlib, datetime
SRC = os.environ.get("FERTIG_SRC", "/workspace/fertig")
APP = os.environ.get("FERTIG_APP", "/workspace/fertig-app/public")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

def write(name, rows, fields):
    os.makedirs(OUT, exist_ok=True)
    json.dump(rows, open(f"{OUT}/{name}.json", "w"), ensure_ascii=False, indent=1)
    with open(f"{OUT}/{name}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore"); w.writeheader()
        for r in rows: w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})

def pid(r): return hashlib.sha1(((r.get("url") or "") + "|" + r["name"] + "|" + r["store"]).encode()).hexdigest()[:12]
def date_of(s):
    m = re.search(r"(20\d\d-\d\d-\d\d)", s or ""); return m.group(1) if m else None

def main():
    d = json.load(open(f"{APP}/data.json")); rows = d["rows"]
    prods, prices, nut, seen = [], [], [], set()
    for r in rows:
        if not r.get("name") or not r.get("store"): continue
        i = pid(r)
        if i in seen: continue
        seen.add(i)
        prods.append({"product_id": i, "name": r["name"], "brand": r.get("brand"), "chain": r["store"], "dish": r.get("dish"),
            "storage": r.get("pack"), "pack_size_g": r.get("size"), "producer": (r.get("herst") or "").split("\n")[0] or None,
            "origin": r.get("origin"), "bio": r.get("bio"), "vegan": r.get("vegan"), "url": r.get("url"), "image_url": r.get("img"),
            "source": r.get("src")})
        if r.get("price") is not None:
            prices.append({"product_id": i, "chain": r["store"], "price_eur": r["price"], "price_per_kg_eur": r.get("ppk"),
                "price_status": r.get("pstat"), "fetched_at": date_of(r.get("psrc")) or date_of(" ".join(q.get("new") or "" for q in r.get("qa") or [] if isinstance(q.get("new"), str))),
                "price_source": r.get("psrc") or (f"{r.get('src')} ({r.get('pstat') or 'Status unbekannt'})" if r.get("src") else None)})
        if any(r.get(k) is not None for k in ("kcal", "p100", "salt")):
            nut.append({"product_id": i, "kcal_100g": r.get("kcal"), "protein_100g": r.get("p100"), "fat_100g": r.get("fat"),
                "saturated_fat_100g": r.get("sat"), "carbs_100g": r.get("carbs"), "sugar_100g": r.get("sugar"), "fiber_100g": r.get("fib"),
                "salt_100g": r.get("salt"), "nutri_score": r.get("ns"), "health_score": r.get("score"), "eur_per_10g_protein": r.get("ppe")})
    write("products", prods, list(prods[0]))
    write("prices", prices, list(prices[0]))
    write("nutrition", nut, list(nut[0]))
    prod = []
    for p in d.get("producers", []):
        prod.append({"slug": p["slug"], "name": p["name"], "website": p.get("website"), "group": p.get("group"),
            "plants": [x["address"] for x in p.get("plants") or []], "approval_codes": [x.get("approval_code") for x in p.get("plants") or []],
            "retail_brands": p.get("retail"), "logo": p.get("logo")})
    write("producers", prod, list(prod[0]))
    ov = json.load(open(f"{SRC}/ovis_codes.json"))
    est = [{"approval_code": v["code"], "company": v["company"], "street": v.get("street"), "postcode": v.get("postcode"), "town": v.get("town"),
            "state": v.get("state"), "list": v.get("list"), "source": "https://vis.statistik.at/fileadmin/ovis/pdf/index.html"} for v in ov.values()]
    write("establishments", est, list(est[0]))
    bt = json.load(open(f"{SRC}/analysis/brand_tree.json"))
    json.dump(bt, open(f"{OUT}/brand_tree.json", "w"), ensure_ascii=False, indent=1)
    lg = json.load(open(f"{SRC}/analysis/logos.json"))
    logos = [{"slug": k, "name": v.get("name"), "category": v.get("logo_category"), "file": v.get("file"), "source_url": v.get("source"),
              "brands": v.get("brands")} for k, v in lg.items()]
    write("logos", logos, list(logos[0]))
    meta = {"exported_at": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "app_generated": d.get("generated"),
            "counts": {"products": len(prods), "prices": len(prices), "nutrition": len(nut), "producers": len(prod), "establishments": len(est), "logos": len(logos)}}
    json.dump(meta, open(f"{OUT}/_meta.json", "w"), indent=1)
    print(meta)
if __name__ == "__main__": main()
