#!/usr/bin/env python3
"""T1402: GTIN backfill bofrost* from Open Food Facts. bofrost pack barcodes embed the
5-digit bofrost article no. (0PPPP69AAAAAC); filled only when that article no. equals the
bofrost.at article no., name + net weight match and nutrition/100 g agrees (±5%) where
OFF publishes it. GOURMET Daheim: 0 matches. Input: raw/gtin_bofrost_gourmet_2026-10-25T1402.json."""
import csv, json, pathlib, collections, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV = ROOT / "data/online_mealprep.csv"
RAW = json.load(open(ROOT / "raw/gtin_bofrost_gourmet_2026-10-25T1402.json", encoding="utf-8"))
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
codes = [m["code"] for m in RAW["bofrost"]["filled"]]
assert len(codes) == len(set(codes)), "duplicate code"
g = 0
for m in RAW["bofrost"]["filled"]:
    code, a = m["code"], m["at_article"]
    assert gs1(code) and len(code) == 13, code
    assert code[7:12] == a, (code, a)
    assert code not in existing, ("collision", code)
    hits = [r for r in rows if r["brand"] == "bofrost*" and re.search(rf"_{a}\.html$", r["url"])]
    assert len(hits) == 1, (a, len(hits))
    r = hits[0]
    assert not r["ean"] and r["name"] == m["row"], r["name"]
    r["ean"] = code; g += 1
    note = f"GTIN lt. Open Food Facts (bofrost Art.-Nr. {a} im Barcode; {m['evidence']}) 2026-10-25"
    f = r["nut_flag"].replace("; keine GTIN", "")
    r["nut_flag"] = (f + "; " + note) if f else note

w = csv.DictWriter(open(CSV, "w", encoding="utf-8", newline=""), fieldnames=fields)
w.writeheader(); w.writerows(rows)
print(f"gtin filled {g}")
