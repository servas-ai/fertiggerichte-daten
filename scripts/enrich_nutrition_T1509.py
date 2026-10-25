"""T1509: nutrition backfill for 19 fairkocht rows sold via Bauernladen.at, from the producer's own shop.
Input: raw/fairkocht_store_api_2026-10-25T1509.json (fairkocht.at WooCommerce Store API, public, robots allow).
Gate: same producer, same product name (manual map), identical price; per-100 g values only as printed
('Nährwerte je 100 g'); Atwater check ±15 %. Bauernladen jar volume (720 ml) vs fairkocht fill (680 ml) noted."""
import csv, html, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; CSV = ROOT / "data/online_mealprep.csv"
API = json.load(open(ROOT / "raw/fairkocht_store_api_2026-10-25T1509.json", encoding="utf-8"))
MAP = {"Bregenzerwälder Käsesuppe": "Bregenzerwälder Bergkäsesuppe", "Kartoffel-Sellerie-Suppe": "Kartoffel Sellerie Suppe, vegan",
       "Kartoffelgulasch": "Kartoffelgulasch, vegie", "Kohlsuppe": "Kohlsuppe, vegie", "Kürbis-Curry-Suppe": "Kürbis Curry Suppe, vegan",
       "Rote Linsen-Curry Suppe": "Rote Linsen – Curry Suppe", "Tomatisierte Karottensuppe": "Tomatisierte Karottensuppe, vegan"}
def txt(p): return html.unescape(re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", p["description"] + " " + p["short_description"])))
def num(pat, t):
    m = re.search(pat + r"\D{0,40}?(\d+(?:,\d+)?)\s*g", t, re.I); return float(m.group(1).replace(",", ".")) if m else None
src = {}
for p in API:
    t = txt(p)
    if "je 100 g" not in t: continue
    blk = t[t.find("Nährwerte je 100 g"):][:400]
    k = re.search(r"(\d+)\s*kJ\s*/\s*(\d+)\s*kcal", blk)
    if not k: continue
    v = {"kcal_100": float(k.group(2)), "fat_100": num(r"FETT", blk), "satfat_100": num(r"gesättigte Fettsäuren", blk),
         "carbs_100": num(r"KOHLENHYDRATE", blk), "sugar_100": num(r"Zucker", blk), "protein_100": num(r"EIWEISS", blk),
         "salt_100": num(r"SALZ", blk)}
    size = re.search(r"Größe:\s*(\d+)\s*(ml|g)", t)
    src[html.unescape(p["name"])] = (v, int(p["prices"]["price"]) / 100, size.group(0) if size else "", p["permalink"])
rows = list(csv.DictReader(open(CSV, encoding="utf-8"))); fields = list(rows[0].keys())
def f(x):
    try: return float(x)
    except (TypeError, ValueError): return None
log = []; skipped = []
for r in rows:
    if r["store"] != "Online: Bauernladen.at" or "fairkocht" not in r["manufacturer"] or r["kcal_100"].strip(): continue
    name = MAP.get(r["name"], r["name"]); s = src.get(name)
    if not s: print("NO MATCH", r["name"]); continue
    v, price, size_txt, url = s
    assert abs(price - f(r["price_eur"])) < 0.005, (r["name"], price, r["price_eur"])
    assert None not in (v["protein_100"], v["fat_100"], v["carbs_100"]), (name, v)
    atw = 4 * v["protein_100"] + 9 * v["fat_100"] + 4 * v["carbs_100"]
    if not (abs(atw - v["kcal_100"]) / v["kcal_100"] < 0.15 or v["kcal_100"] < 30 and abs(atw - v["kcal_100"]) < 6):
        print("SKIP Atwater", r["name"], v, round(atw)); skipped.append(r["name"]); continue
    for a, x in v.items(): r[a] = "" if x is None else f"{x:.1f}"
    size, pr = f(r["size_g"]), v["protein_100"]
    if size:
        r["kcal_pack"] = str(round(v["kcal_100"] * size / 100)); r["protein_pack"] = f"{pr * size / 100:.1f}"
        if pr: r["eur_per_10g_protein"] = f"{f(r['price_eur']) / (pr * size / 1000):.2f}"
    r["nut_source"] = f"fairkocht.at Produktseite (Hersteller, '{name}') Nährwerte je 100 g, 2026-10-25"
    r["nut_flag"] = r["nut_flag"].replace("keine Nährwerte je 100 g auf bauernladen.at (nicht geschätzt)", "bauernladen.at nennt keine Nährwerte; Werte vom Hersteller fairkocht.at")
    note = f"Hersteller nennt {size_txt}" if size_txt and size_txt.split()[-2] != str(int(size or 0)) else ""
    r["nut_flag"] = (r["nut_flag"] + "; " + note).strip("; ") if note else r["nut_flag"]
    log.append((r["name"], v["kcal_100"], v["protein_100"], round(atw), size_txt))
# flag products the producer publishes with identical value sets (likely copied table)
from collections import defaultdict
same = defaultdict(list)
for r in rows:
    if r["nut_source"].startswith("fairkocht.at"): same[tuple(r[k] for k in ("kcal_100", "fat_100", "carbs_100", "protein_100", "salt_100"))].append(r)
for g in same.values():
    if len(g) > 1:
        for r in g:
            o = ", ".join(x["name"] for x in g if x is not r)
            r["nut_flag"] = (r["nut_flag"] + f"; Hersteller veröffentlicht identische Nährwerte wie {o}").strip("; ")
w = csv.DictWriter(open(CSV, "w", encoding="utf-8", newline=""), fieldnames=fields); w.writeheader(); w.writerows(rows)
for l in log: print(*l, sep=" | ")
print("filled", len(log))
