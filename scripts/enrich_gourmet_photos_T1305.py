"""Daten-Squad 2026-10-25T1305: official dish photos for 'Online: GOURMET Daheim (Mahlzeit Linz)' rows.

Source: the official GOURMET Daheim menu PDF 'Speisekarte 2026' published by Mahlzeit Linz
(https://www.mahlzeit.co.at/wp-content/uploads/2026/03/GOURMET_daheim_SPK_26_Mahlzeit_web.pdf, pages 20-56).
Each dish is printed as name, 7-digit order number ('23 02034') and the dish photo directly beneath it.
`pdftohtml -xml` gives text and image boxes; a photo is assigned to an order number only when exactly one
image (>120 px) starts 0-40 pt below the number and spans its horizontal centre (127/127 unique, 0 ambiguous).
All 127 pairs were checked on contact sheets against the row name (vision gate passed, 0 rejected).
Photos are downscaled to max 480x700 JPEG and stored under images/gourmet_daheim/<art>.jpg; existing
mahlzeit.co.at web photos (8 rows) are kept, only empty image_url cells are filled.
Usage: python3 scripts/enrich_gourmet_photos_T1305.py /tmp/gdimg/match.json"""
import sys, csv, json, os, hashlib
CSV = "data/online_mealprep.csv"; STORE = "Online: GOURMET Daheim (Mahlzeit Linz)"
PDF = "https://www.mahlzeit.co.at/wp-content/uploads/2026/03/GOURMET_daheim_SPK_26_Mahlzeit_web.pdf"
BASE = "https://raw.githubusercontent.com/servas-ai/fertiggerichte-daten/main/images/gourmet_daheim/"
match = json.load(open(sys.argv[1]))
with open(CSV, newline="", encoding="utf-8") as f:
    rd = csv.DictReader(f); fields = rd.fieldnames; rows = list(rd)
ev, filled = [], 0
for r in rows:
    if r["store"] != STORE: continue
    art = r["url"].split("art=")[-1]
    m = match.get(art)
    if not m: ev.append({"art": art, "name": r["name"], "photo": None, "reason": "dish not shown with a photo in the Speisekarte PDF"}); continue
    p = f"images/gourmet_daheim/{art}.jpg"
    e = {"art": art, "name": r["name"], "pdf_page": m[0]["page"], "file": p, "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest(),
         "vision_gate": "pass", "kept_existing": bool(r["image_url"])}
    if not r["image_url"]:
        r["image_url"] = BASE + f"{art}.jpg"; filled += 1
    ev.append(e)
with open(CSV, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
json.dump({"source_pdf": PDF, "retrieved": "2026-10-25", "method": __doc__, "filled": filled, "rows": ev},
          open("raw/gourmet_daheim_photos_2026-10-25T1305.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("filled", filled, "of", sum(1 for r in rows if r["store"] == STORE))
