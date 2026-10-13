"""Daten-Squad 2026-10-13T18 logo merge: Subway (largest logo-less brand, 59 products).
Additive only. Vision gate: rendered PNG preview inspected (scripts/logo_work_T18/subway_preview.png):
yellow 'SUB' + green 'WAY' wordmark with arrow terminals = current Subway logo (2016), sharp, no photo, works on light bg."""
import json, shutil, os, csv

G = "Vision gate 2026-10-13T18 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T18")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

NEW = [
    ("subway", "Subway", ["Subway", "SUBWAY", "Subway®"], "subway.svg",
     "https://commons.wikimedia.org/wiki/File:Subway_2016_logo.svg",
     "Wikimedia Commons File:Subway 2016 logo.svg (Public domain – Textlogo/Schwelle der Schöpfungshöhe; Hinweis 'trademarked'; Urheber Subway IP LLC; "
     "Original https://upload.wikimedia.org/wikipedia/commons/5/5c/Subway_2016_logo.svg, 1702 B, unverändert)", True),
    ("alpenhain", "Alpenhain", ["Alpenhain", "ALPENHAIN", "Alpenhain Back"], "alpenhain.png",
     "https://commons.wikimedia.org/wiki/File:Alpenhain_Logo.png",
     "Wikimedia Commons File:Alpenhain Logo.png (CC BY-SA 4.0, Robert Winkelmann; Quelle alpenhain.de) – Alpenhain Käsespezialitäten GmbH (Brand-Tree-Konzern); "
     "2016×1142 RGBA auf 512×290 verkleinert, sonst unverändert", True),
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
    d[slug] = dict(slug=slug, name=name, brands=brands, logo_category=("Handelskette" if slug == "subway" else "Markenhersteller"), file="logos/" + fn,
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
