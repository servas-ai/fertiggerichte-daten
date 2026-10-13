"""Daten-Squad 2026-10-13T22 logo merge: HelloFresh (largest logo-less brand, 93 products).
Additive only. Vision gate: rendered PNG preview inspected (scripts/logo_work_T22/hellofresh_preview.png):
lime fruit icon + 'Hello' script + 'FRESH' bold sans = official HelloFresh horizontal lockup (#91C11E),
sharp, transparent BG, no photo, works on light UI bg."""
import json, shutil, os, csv

G = "Vision gate 2026-10-13T22 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T22")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

NEW = [
    ("hellofresh", "HelloFresh", ["HelloFresh", "Hello Fresh", "HelloFresh SE"], "hellofresh.svg",
     "https://cdn.hellofresh.com/logo/HelloFresh_Logo_Horizontal_V2.svg",
     "offizielles CDN-Asset HelloFresh_Logo_Horizontal_V2.svg (cdn.hellofresh.com/logo/; robots.txt hellofresh.de/.com erlauben CDN-Logo; "
     "kein Commons-Logo vorhanden; Wikipedia-Datei nur fair-use/Bild-LogoSH → nicht verwendet; "
     "13746 B SVG unverändert, title HelloFresh_RGB_2C_Horizontal, fill #91C11E)", True),
]

d = json.load(open(P))
added = []
for slug, name, brands, fn, src, orig, hq in NEW:
    sp = os.path.join(FINAL, fn); assert os.path.exists(sp), sp
    if slug in d and d[slug].get("file") and os.path.exists("/workspace/fertig/analysis/" + d[slug]["file"]):
        print("skip existing file-backed", slug); continue
    dest = os.path.join(LOGOS_DIR, fn)
    assert not os.path.exists(dest), "file name collision " + fn
    shutil.copy(sp, dest)
    d[slug] = dict(slug=slug, name=name, brands=brands, logo_category="Online-Mealprep", file="logos/" + fn,
                   source=src, size=fn.rsplit(".", 1)[-1], note=f"{G} · {orig}", hq=hq)
    added.append(slug)

tmp = P + ".tmp"; json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, P)

logos_rows = [{"slug": k, "name": v.get("name"), "category": v.get("logo_category"), "file": v.get("file"),
               "source_url": v.get("source"), "brands": v.get("brands")} for k, v in d.items()]
json.dump(logos_rows, open(f"{DATEN}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{DATEN}/data/logos.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, ["slug", "name", "category", "file", "source_url", "brands"]); w.writeheader()
    for r in logos_rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
print("added", added, "total", len(d))
# verify
assert os.path.exists(os.path.join(LOGOS_DIR, "hellofresh.svg"))
assert d["hellofresh"]["file"] == "logos/hellofresh.svg"
print("ok hellofresh wired")
