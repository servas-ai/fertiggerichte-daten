"""Daten-Squad 2026-10-16T2139 logo merge: store logo for the new online store myProduct (T2111).
Vision gate: final file rendered and inspected via Read (correct wordmark, legible, not a placeholder)."""
import json, shutil, os, datetime, csv, hashlib, collections

G = "Vision gate 2026-10-16T2139 (Daten-Squad): visuell geprüft (korrekte Marke, lesbar, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T2139")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

NEW = [
    ("myproduct", "myProduct", ["myProduct", "myProduct.at", "myproduct.at", "myProduct GmbH", "Online: myProduct"], "myproduct.png",
     "https://myproduct.at/media/logo/default/myproductatlogo.png (myproduct.at header/cookie-banner <img alt='Logo myProduct.at'>; robots allow /media/)",
     "Offizielles 'myProduct.at'-Logo (grün-pinkes Blatt-Signet, graues 'my' + pinkes 'Product' + '.at' in pinkem Rahmen) von myproduct.at, unverändert 520x162 RGBA; Betreiber myProduct GmbH, Zwettl, FN 431059k", True, "Handelskette"),
]

ALIASES = {}

REJECTED = {
    "myproduct.at schema.org Organization.logo (theme images/logo.svg)": "renders as the 'MageSuite.io' theme-vendor wordmark (Magento theme placeholder), not the myProduct brand → rejected",
    "Hartl's Kulinarikum": "site shows only photo header banners (header_web_hartls2), no standalone logo asset → no logo",
    "BioArt AG": "only 198x45 / 70x92 header rasters on bioart.at → too small, deferred",
    "Rapunzel": "rapunzel.de header exposes only icon SVGs (no wordmark asset URL in HTML) → deferred",
}

VISION = {"myproduct": "PASS — myProduct.at wordmark with green leaf mark and pink frame (PNG 520x162 RGBA, readable on white)"}

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
    w = csv.DictWriter(fh, fields); w.writeheader()
    for r in logos_rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})

bc = collections.Counter()
with open(f"{DATEN}/data/products.csv") as fh:
    for row in csv.DictReader(fh):
        bc[(row.get("brand") or "").strip()] += 1
impact = {slug: sum(bc.get(b, 0) for b in d[slug]["brands"]) for slug in added + updated}

evidence = {
    "run": "2026-10-16T2139 Daten-Squad",
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
ev = f"{DATEN}/raw/logos_squad_2026-10-16T2139.json"
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
