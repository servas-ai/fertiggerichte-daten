#!/usr/bin/env python3
"""T1207: GTIN backfill from Shopify per-product JSON (variant.barcode) and
nutrition backfill for identical GTINs published elsewhere (MPreis / OFF).
Input: raw/shopify_barcodes_2026-10-25T1207.json. Only published values; no estimates."""
import csv, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV = ROOT / "data/online_mealprep.csv"
RAW = json.load(open(ROOT / "raw/shopify_barcodes_2026-10-25T1207.json", encoding="utf-8"))
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
fields = list(rows[0].keys())

def fmt(v):
    return str(round(float(v), 2))

import re
def norm(t):
    return re.sub(r"\s+", " ", t).strip()

def find(store, name=None, url=None):
    hits = [r for r in rows if r["store"] == store and
            ((url and r["url"].rstrip("/").split("/")[-1] == url.rstrip("/").split("/")[-1]) or
             (name and norm(name).endswith(norm(r["name"]))))]
    assert len(hits) == 1, (store, name, url, len(hits))
    return hits[0]

g = n = 0
for x in RAW["gtin"]:
    r = find(x["store"], url=x["url"])
    if r["ean"] and r["ean"] != x["gtin"]:
        raise SystemExit(f"conflict {r['name']}: {r['ean']} vs {x['gtin']}")
    if not r["ean"]:
        r["ean"] = x["gtin"]; g += 1
        note = "GTIN lt. Shopify-Produkt-JSON (variant barcode, Prüfziffer ok) 2026-10-25"
        f = r["nut_flag"].replace("keine Nährwerte/GTIN im Shop veröffentlicht", "keine Nährwerte im Shop veröffentlicht")
        f = f.replace("; keine GTIN", "")
        r["nut_flag"] = (f + "; " + note) if f else note

for x in RAW["nutrition"]:
    r = find(x["store"], name=x["row_name"])
    assert not r["kcal_100"], r["name"]
    r.update(kcal_100=fmt(float(x["kcal"])), protein_100=fmt(x["protein"]), fat_100=fmt(x["fat"]),
             satfat_100=fmt(x["satfat"]), carbs_100=fmt(x["carbs"]), sugar_100=fmt(x["sugar"]),
             salt_100=fmt(x["salt"]))
    if not r["ean"]:
        r["ean"] = x["gtin"]; g += 1
    size = float(r["size_g"] or 0)
    if size:
        pp = round(x["protein"] * size / 100, 1)
        r["protein_pack"] = fmt(pp); r["kcal_pack"] = str(round(x["kcal"] * size / 100))
        if r["price_eur"] and pp:
            r["eur_per_10g_protein"] = fmt(round(float(r["price_eur"]) / pp * 10, 2))
    r["nut_source"] = x["src"] + " (abgerufen 2026-10-25)"
    flag = f"Nährwerte je 100 g über identische GTIN {x['gtin']} übernommen, Atwater {x['atwater_dev_pct']:+.1f} % ok"
    r["nut_flag"] = flag
    n += 1

w = csv.DictWriter(open(CSV, "w", encoding="utf-8", newline=""), fieldnames=fields)
w.writeheader(); w.writerows(rows)
print(f"gtin filled {g}, nutrition filled {n}")
