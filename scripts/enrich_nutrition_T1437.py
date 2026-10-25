#!/usr/bin/env python3
"""T1437: nutrition backfill by identical GTIN for online rows without nutrition
(myProduct multipacks: dm/Gurkerl retail row first, else Open Food Facts), plus
Leitgeb's GTIN from identical Gurkerl rows (brand + name + 450 g + nutrition).
Input: raw/off_nutrition_lookup_2026-10-25T1437.json (OFF product API v2). Only published values."""
import csv, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV = ROOT / "data/online_mealprep.csv"
OFF = json.load(open(ROOT / "raw/off_nutrition_lookup_2026-10-25T1437.json", encoding="utf-8"))
rows = list(csv.DictReader(open(CSV, encoding="utf-8"))); fields = list(rows[0].keys())
prod = {p["ean"]: p for p in csv.DictReader(open(ROOT / "data/products.csv", encoding="utf-8")) if p["ean"]}
nut = {n["product_id"]: n for n in csv.DictReader(open(ROOT / "data/nutrition.csv", encoding="utf-8"))}
# skipped on purpose: name/size mismatch between shop row and OFF entry
SKIP = {"4280001516625": "OFF-Name 'Kürbissuppe mit Karotten und Kartoffeln' ≠ 'mit Kokos'",
        "4031829232408": "OFF 385 ml ≠ Shop 400 g",
        "4260655551203": "OFF 'Rote Linsen Suppe mit Kokos' ≠ 'Orientalisch'",
        "4260655551180": "OFF 'Kartoffelsuppe' ≠ 'Kartoffel Petersilie'"}
DRY = {"4020943134309", "8856848001318", "8856848001325", "8856848001370"}
K = [("kcal_100", "energy-kcal_100g", "kcal_100g"), ("protein_100", "proteins_100g", "protein_100g"),
     ("fat_100", "fat_100g", "fat_100g"), ("satfat_100", "saturated-fat_100g", "saturated_fat_100g"),
     ("carbs_100", "carbohydrates_100g", "carbs_100g"), ("sugar_100", "sugars_100g", "sugar_100g"),
     ("fiber_100", "fiber_100g", "fiber_100g"), ("salt_100", "salt_100g", "salt_100g")]
def f(v):
    try: return float(v)
    except (TypeError, ValueError): return None
filled = []; log = []
for r in rows:
    e = r["ean"].strip()
    if r["kcal_100"].strip() or not e or e in SKIP or r["store"] != "Online: myProduct": continue
    p = prod.get(e); n = nut.get(p["product_id"]) if p else None
    o = ((OFF.get(e) or {}).get("product") or {}).get("nutriments") or {}
    if n and f(n["kcal_100g"]) is not None:
        vals = {a: f(n[c]) for a, _, c in K}; src = f"{p['chain']} Produktdaten (identische GTIN {e}) je 100 g, 2026-10-25"
        ok = f(o.get("energy-kcal_100g"))
        note = (f"; OFF {e}: {ok:g} kcal/100 g (Abweichung zur Handelsangabe, ältere Rezeptur?)" if ok and abs(ok - vals['kcal_100']) / vals['kcal_100'] > .05 else "")
    elif f(o.get("energy-kcal_100g")) is not None:
        vals = {a: f(o.get(b)) for a, b, _ in K}; src = f"Open Food Facts {e} (identische GTIN) je 100 g, 2026-10-25"; note = ""
    else: continue
    kc, pr, fa, ca = vals["kcal_100"], vals["protein_100"], vals["fat_100"], vals["carbs_100"]
    atw = 4 * pr + 9 * fa + 4 * ca + 2 * (vals["fiber_100"] or 0)
    assert abs(atw - kc) / kc < 0.15, (e, atw, kc)
    for a, _, _ in K: r[a] = "" if vals[a] is None else (f"{vals[a]:.1f}" if a != "kcal_100" else f"{round(vals[a]):.1f}")
    size, price = f(r["size_g"]), f(r["price_eur"])
    if size:
        r["kcal_pack"] = str(round(kc * size / 100)); r["protein_pack"] = f"{pr * size / 100:.1f}"
        if price and pr: r["eur_per_10g_protein"] = f"{price / (pr * size / 1000):.2f}"
    r["nut_source"] = src
    fl = ("Nährwerte je 100 g Trockenprodukt" if e in DRY else "") + note
    fl = fl.lstrip("; ")
    r["nut_flag"] = fl
    filled.append(e); log.append((e, r["name"][:50], src.split(" (")[0], kc))
# Leitgeb's: GTIN from identical Gurkerl rows
LG = {"Italienischer Nudelteller": "9120071330262", "Gemischter Nudelteller": "9120071330255",
      "Kärntner Käsnudel": "9120071330019", "Kärntner Käsnudel Vegan": "9120071330965"}
used = {x["ean"] for x in rows if x["ean"]}
g = 0
for r in rows:
    if r["store"] == "Online: Leitgeb's Kärntnernudel" and r["name"] in LG and not r["ean"]:
        c = LG[r["name"]]; assert c not in used and prod[c]["chain"] == "Gurkerl" and prod[c]["pack_size_g"] == "450.0"
        r["ean"] = c; g += 1
        note = "GTIN lt. identischem Gurkerl-Artikel (Leitgeb's, gleicher Name, 450 g) 2026-10-25"
        if r["name"] == "Gemischter Nudelteller": note += "; Gurkerl nennt 196 kcal statt 186 kcal (übrige Nährwerte identisch)"
        if r["name"] == "Kärntner Käsnudel Vegan": note += "; Gurkerl-Nährwerte identisch mit nicht-veganer Käsnudel → nicht übernommen"
        r["nut_flag"] = (r["nut_flag"] + "; " + note).lstrip("; ")
w = csv.DictWriter(open(CSV, "w", encoding="utf-8", newline=""), fieldnames=fields); w.writeheader(); w.writerows(rows)
for l in log: print(*l, sep=" | ")
print(f"nutrition filled {len(filled)}; leitgeb gtin {g}")
