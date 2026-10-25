#!/usr/bin/env python3
"""T1339: GTIN backfill — Wiesbauer Gourmet from product-page JSON-LD gtin (19),
Egle from Open Food Facts (own GS1 prefix 4262468, unique names, 2 nutrition-identical).
Input: raw/gtin_wiesbauer_egle_2026-10-25T1339.json. Only published values."""
import csv, json, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV = ROOT / "data/online_mealprep.csv"
RAW = json.load(open(ROOT / "raw/gtin_wiesbauer_egle_2026-10-25T1339.json", encoding="utf-8"))
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
fields = list(rows[0].keys())

def gs1(c):
    if not c.isdigit() or len(c) not in (8, 12, 13, 14): return False
    d = [int(x) for x in c]
    s = sum(v * (3 if i % 2 == 0 else 1) for i, v in enumerate(reversed(d[:-1])))
    return (10 - s % 10) % 10 == d[-1]

existing = collections.Counter(r["ean"] for r in rows if r["ean"])
for p in csv.DictReader(open(ROOT / "data/products.csv", encoding="utf-8")):
    if p["ean"]: existing[p["ean"]] += 1

todo = []
for x in RAW["wiesbauer"]["rows"]:
    if x["jsonld"] and x["jsonld"][0][1]:
        todo.append(("Online: Wiesbauer Gourmet", x["url"], None, x["jsonld"][0][1],
                     "GTIN lt. Produktseite JSON-LD (gtin, Prüfziffer ok) 2026-10-25"))
for m in RAW["egle"]["matches"]:
    todo.append(("Online: Egle", None, m["row"], m["gtin"],
                 "GTIN lt. Open Food Facts (Marke Egle, Präfix 4262468; " + m["evidence"] + ") 2026-10-25"))
codes = [t[3] for t in todo]
assert len(codes) == len(set(codes)), "duplicate code"
g = 0
for store, url, name, code, note in todo:
    assert gs1(code), code
    assert code not in existing, ("collision", code)
    hits = [r for r in rows if r["store"] == store and ((url and r["url"] == url) or (name and r["name"] == name))]
    assert len(hits) == 1, (store, url, name, len(hits))
    r = hits[0]
    assert not r["ean"], r["name"]
    r["ean"] = code; g += 1
    f = r["nut_flag"].replace("; keine GTIN", "")
    r["nut_flag"] = (f + "; " + note) if f else note

w = csv.DictWriter(open(CSV, "w", encoding="utf-8", newline=""), fieldnames=fields)
w.writeheader(); w.writerows(rows)
print(f"gtin filled {g}")
