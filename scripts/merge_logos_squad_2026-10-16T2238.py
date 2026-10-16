"""Daten-Squad 2026-10-16T2238 logo merge: producer/brand logos for the myProduct.at producers added T2139 (Rapunzel, ARCHE, EgeSun, Sanchon, Petersilchen).
Vision gate: final file rendered and inspected via Read (correct wordmark, legible, not a placeholder)."""
import json, shutil, os, datetime, csv, hashlib, collections

G = "Vision gate 2026-10-16T2238 (Daten-Squad): visuell geprüft (korrekte Marke, lesbar, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T2238")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

NEW = [
    ("rapunzel", "Rapunzel", ["Rapunzel", "RAPUNZEL", "Rapunzel Naturkost", "Rapunzel Naturkost GmbH & Co. KG"], "rapunzel.svg",
     "https://commons.wikimedia.org/wiki/File:Rapunzel_Naturkost.svg (upload.wikimedia.org/wikipedia/commons/b/b2/Rapunzel_Naturkost.svg; Commons: Public domain, source rapunzel.de warenkunde PDF)",
     "Offizielles RAPUNZEL-Wortbild (grüne Schrift auf gelbem Oval, grüner Rahmen), Commons-SVG unverändert 516x173; Rapunzel Naturkost GmbH & Co. KG, Legau (LEI, HRA 14236)", True, "Markenhersteller"),
    ("arche", "ARCHE Naturküche", ["Arche", "ARCHE", "Arche Naturküche", "ARCHE Naturküche", "Arche Naturprodukte GmbH", "ARCHE Naturprodukte GmbH"], "arche.png",
     "https://www.arche-naturkueche.de/_img/arche-logo.png (header <img> on arche-naturkueche.de, robots allow)",
     "Offizielles 'ARCHE NATURKÜCHE'-Logo (rote Sonne über Bogen, schwarzer Schriftzug), unverändert 140x115 RGB (klein, einzige Header-Datei); ARCHE Naturprodukte GmbH, Hilden (LEI, HRB 85754)", False, "Markenhersteller"),
    ("egesun", "EgeSun", ["EgeSun", "EGESUN", "EgeSun GmbH & Co. KG"], "egesun.png",
     "https://www.egesun.de/wp-content/uploads/2025/09/egesun-logo-s.png (header <img alt=logo> on egesun.de, robots allow)",
     "Offizielles 'EgeSun – ORGANIC SINCE 1979'-Wortbild (dunkelbraun, Sonnenstrahlen), unverändert 399x142 RGBA; Firmenlogo der EgeSun GmbH & Co. KG, Oyten (Marke Vegan Pete hat eigenes Logo, hier NICHT zugeordnet)", True, "Markenhersteller"),
    ("sanchon", "Sanchon", ["Sanchon", "SANCHON"], "sanchon.png",
     "https://petersilchen.de/wp-content/uploads/2017/02/sanchon-logo-200px.png (petersilchen.de brand section <img>, robots allow)",
     "Offizielles SANCHON-Markenlogo (schwarzer Eselkopf + Serifen-Schriftzug), unverändert 200x137 RGB; Marke der Petersilchen GmbH, Steinheim", False, "Marke"),
    ("petersilchen", "Petersilchen", ["Petersilchen", "PETERSILCHEN", "Petersilchen GmbH"], "petersilchen.png",
     "https://petersilchen.de/wp-content/uploads/2021/08/petersilchen_logo_rgb-1.png (petersilchen.de header logo, robots allow)",
     "Offizielles 'PETERSILCHEN Biologische Feinkost'-Firmenlogo (grün-gelber Bogen, graue Schrift), unverändert 210x75 RGBA; Petersilchen GmbH, Steinheim (HRB 11924)", False, "Markenhersteller"),
]

ALIASES = {}

REJECTED = {
    "rettergut.de": "robots.txt disallows our UA for the homepage → not fetched, no logo",
    "Zwergenwiese (Rapunzel brand)": "zwergenwiese.de HTML exposes no logo <img>/schema logo; no Commons file → no logo (Rapunzel parent logo NOT reused for the sub-brand)",
    "Vegan Pete (EgeSun brand)": "veganpete.de 404; EgeSun company logo NOT reused as the Vegan Pete brand logo",
    "De Rit / BioArt / Perfect Earth": "derit.nl, bioart.at, perfectearth.eu robots.txt unreachable (TLS EOF) → treated as disallow, not fetched",
    "Hartl's Kulinarikum": "hartls-kulinarikum.at shows only photo banners, no logo asset (re-checked T2238)",
    "petersilchen.de partner badges (Patentabfrage, COMPANY BALANCED)": "third-party certification badges, not the brand → rejected",
}

VISION = {
    "rapunzel": "PASS — RAPUNZEL green wordmark on yellow rounded badge (SVG rendered 600 px via rsvg-convert, legible)",
    "arche": "PASS — ARCHE NATURKÜCHE wordmark with red sun (140x115, small but legible on white)",
    "egesun": "PASS — EgeSun wordmark 'ORGANIC SINCE 1979' (399x142, transparent, legible on white)",
    "sanchon": "PASS — SANCHON donkey head + serif wordmark (200x137, legible)",
    "petersilchen": "PASS — PETERSILCHEN 'Biologische Feinkost' wordmark with green/yellow arc (210x75, legible)",
}

d = json.load(open(P))
added, updated = [], []
sha = {}
for slug, name, brands, fn, src, orig, hq, cat in NEW:
    sp = os.path.join(FINAL, fn); assert os.path.exists(sp), sp
    with open(sp, "rb") as fh: sha[slug] = hashlib.sha256(fh.read()).hexdigest()
    entry = dict(slug=slug, name=name, brands=brands, logo_category=cat, file="logos/" + fn,
                 source=src, size=fn.rsplit(".", 1)[-1], note=f"{G} · {orig}", hq=hq)
    if slug in d:
        old = d[slug]
        if old.get("file") and os.path.exists("/workspace/fertig/analysis/" + (old["file"] or "")):
            print("skip existing file-backed", slug); continue
        entry["brands"] = list(dict.fromkeys(list(old.get("brands") or []) + brands))
        if old.get("note"): entry["note"] += " · vorher (file-less): " + old["note"][:300]
        dest = os.path.join(LOGOS_DIR, fn)
        assert not os.path.exists(dest), "file name collision " + fn
        shutil.copy(sp, dest); d[slug] = entry; updated.append(slug)
    else:
        dest = os.path.join(LOGOS_DIR, fn)
        assert not os.path.exists(dest), "file name collision " + fn
        shutil.copy(sp, dest); d[slug] = entry; added.append(slug)

aliased = {}
for slug, al in ALIASES.items():
    assert d[slug].get("file"), slug
    before = list(d[slug].get("brands") or [])
    d[slug]["brands"] = list(dict.fromkeys(before + al))
    aliased[slug] = [a for a in al if a not in before]

tmp = P + ".tmp"; json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, P)

logos_rows = [{"slug": k, "name": v.get("name"), "category": v.get("logo_category"), "file": v.get("file"),
               "source_url": v.get("source"), "brands": v.get("brands")} for k, v in d.items()]
json.dump(logos_rows, open(f"{DATEN}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{DATEN}/data/logos.csv", "w", newline="") as fh:
    fields = ["slug", "name", "category", "file", "source_url", "brands"]
    w = csv.DictWriter(fh, fields, lineterminator="\n"); w.writeheader()
    for r in logos_rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})

bc = collections.Counter()
with open(f"{DATEN}/data/products.csv") as fh:
    for row in csv.DictReader(fh):
        bc[(row.get("brand") or "").strip()] += 1
impact = {slug: sum(bc.get(b, 0) for b in d[slug]["brands"]) for slug in added + updated}

evidence = {
    "run": "2026-10-16T2238 Daten-Squad",
    "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
    "added": [
        {"slug": k, "note": d[k]["note"], "source": d[k]["source"], "sha256": sha[k],
         "products_impacted": impact[k], "aliases": d[k]["brands"]}
        for k in added
    ],
    "updated_fileless": [
        {"slug": k, "note": d[k]["note"], "source": d[k]["source"], "sha256": sha[k],
         "products_impacted": impact[k], "aliases": d[k]["brands"]}
        for k in updated
    ],
    "aliases_added": {k: {"aliases": v, "products_impacted": sum(bc.get(b, 0) for b in v)} for k, v in aliased.items()},
    "rejected": REJECTED,
    "vision_gate": VISION,
    "counts": {
        "added": len(added), "updated_fileless": len(updated),
        "total_rows": len(d),
        "with_file": sum(1 for v in d.values() if (v.get("file") or "").strip()),
        "products_impacted_total": sum(impact.values()),
    },
    "sha256": sha,
}
ev = f"{DATEN}/raw/logos_squad_2026-10-16T2238.json"
os.makedirs(f"{DATEN}/raw", exist_ok=True)
json.dump(evidence, open(ev, "w"), ensure_ascii=False, indent=1)
print("added", added)
print("updated_fileless", updated)
print("impact", impact)
print("total", len(d), "with_file", evidence["counts"]["with_file"])
for slug in added + updated:
    assert os.path.exists(os.path.join(LOGOS_DIR, d[slug]["file"].split("/", 1)[1]))
    assert d[slug]["file"]
print("ok")
