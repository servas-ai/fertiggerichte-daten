"""Daten-Squad 2026-10-13T23 logo merge: fill top Eigenmarke/brand gaps via official packshot crops.
Vision gate: each crop inspected via Read (correct brand wordmark, legible, not a product photo /
generic icon). Sources: packshots already in the dataset (SPAR CDN / dm-static / Gurkerl CDN / OFF).
No Aldi CDN Brandpage-Logo re-probe (known 403). No login/cookies/JS-bypass."""
import json, shutil, os, datetime, csv, hashlib

G = "Vision gate 2026-10-13T23 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T23")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

# slug, name, brands, file, source, origin-note, hq, category
NEW = [
    ("good-choice", "Good Choice",
     ["Good Choice", "GOOD CHOICE", "good choice", "Good Choice (Hofer Eigenmarke)"],
     "good-choice.png",
     "OFF packshot GTIN 4099200146256 front_de.15 (GOOD CHOICE Faschierte Laibchen) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt offizielles Hofer/OFF-Produktfoto (GOOD Choice Wordmark im handgezeichneten Oval); Aldi-CDN Brandpage-Logo_* bewusst nicht erneut geprobt (T09 alle 403); Commons kein Treffer",
     True, "Eigenmarke"),
    ("spar-enjoy", "SPAR enjoy",
     ["SPAR enjoy", "Spar enjoy", "Spar Enjoy"],
     "spar-enjoy.png",
     "OFF packshot GTIN 9100000702797 front_de.6 (SPAR enjoy Mediterraner Nudel-Kräuter-Salat) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt SPAR enjoy. Wordmark + SPAR-Baum (weißer Druck auf Karton-Sleeve); spar.at weisses-auf-transparent vorher abgelehnt (T12) — dieser Crop ist auf braunem Karton lesbar; Spar enjoy + SPAR enjoy als Alias gemerged",
     True, "Eigenmarke"),
    ("dmbio", "dmBio",
     ["dmBio"],
     "dmbio.png",
     "dm-static packshot dmBio Gulasch vegan (products.dm-static.com …/dmbio-gulasch-vegan) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt offizielles dm-Produktfoto (grünes dmBio-Siegel mit dm-Untermarke); Commons nur dm-Hauptlogo, kein dmBio; dm.de/marken/dmbio JS-only ohne freigestelltes Asset",
     True, "Eigenmarke"),
    ("chef-select", "Chef Select",
     ["Chef Select", "CHEF SELECT"],
     "chef-select.png",
     "OFF packshot GTIN 4056489009214 front_en.94 (Chef Select Smoked Ham Tortellini) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Lidl Eigenmarke CHEF SELECT (weiße Kapitälchen auf rosa Header); Commons nur Lidl-Hauptlogo / Produktfotos, kein freigestelltes Chef-Select-Asset",
     True, "Eigenmarke"),
    ("chef-menue", "Chef Menü",
     ["Chef Menü", "Chef Menu", "chef menü"],
     "chef-menue.png",
     "OFF packshot GTIN 9010158009856 front_en.4 (Chef Menü Schweinsbraten) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt REWE-AT Eigenmarke Chef Menü (weißes Wordmark auf grünem Blatt + Wirt z'Haus); kein Commons-/CDN-Freisteller",
     True, "Eigenmarke"),
    ("namdong", "Namdong",
     ["Namdong"],
     "namdong.png",
     "Gurkerl CDN packshot Namdong Beef Instant Noodle Pot (cdn.gurkerl.at …/44153-…) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Unilever-Marke namdong + Hangul-Badge; namdong.com / unilever.co.uk Akamai 403 (nicht umgangen); Commons nur Namdong-gu Geo, kein Noodle-Logo",
     True, "Markenhersteller"),
    ("pappudia", "Pappudia",
     ["Pappudia", "Pappudia Handgemacht"],
     "pappudia.png",
     "OFF packshot GTIN 8595643805690 front_cs.12 (Pappudia Hummus) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Lidl Eigenmarke PAPPUDIA (gestapeltes Wordmark + Check-Pin auf Senf-Kreis); Gurkerl-Fertiggericht-Fotos ohne Verpackungslogo; Commons kein Treffer",
     True, "Eigenmarke"),
]

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
        shutil.copy(sp, os.path.join(LOGOS_DIR, fn)); d[slug] = entry; updated.append(slug)
    else:
        dest = os.path.join(LOGOS_DIR, fn)
        assert not os.path.exists(dest), "file name collision " + fn
        shutil.copy(sp, dest); d[slug] = entry; added.append(slug)

tmp = P + ".tmp"; json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, P)

logos_rows = [{"slug": k, "name": v.get("name"), "category": v.get("logo_category"), "file": v.get("file"),
               "source_url": v.get("source"), "brands": v.get("brands")} for k, v in d.items()]
json.dump(logos_rows, open(f"{DATEN}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{DATEN}/data/logos.csv", "w", newline="") as fh:
    fields = ["slug", "name", "category", "file", "source_url", "brands"]
    w = csv.DictWriter(fh, fields); w.writeheader()
    for r in logos_rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})

# product impact
import collections
bc = collections.Counter()
with open(f"{DATEN}/data/products.csv") as fh:
    for row in csv.DictReader(fh):
        bc[(row.get("brand") or "").strip()] += 1
impact = {}
for slug in added + updated:
    brands = d[slug]["brands"]
    impact[slug] = sum(bc.get(b, 0) for b in brands)

evidence = {
    "run": "2026-10-13T23 Daten-Squad",
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
    "aliases_producer_fallback": [],
    "rejected": {
        "Good Choice Aldi CDN Brandpage-Logo_*": "not re-probed — T09 616 GET variants all 403 (policy)",
        "namdong.com / unilever.co.uk brands page": "Akamai Access Denied HTTP 403 — not bypassed",
        "Wikimedia Commons (dmBio/Good Choice/Pappudia/Chef Select/SPAR enjoy/Namdong/Chef Menü)": "no usable logo file (only unrelated / Lidl-main / SPAR-main / Namdong-gu geo)",
        "dm.de/marken/dmbio freigestelltes Logo": "page JS-rendered, no static logo asset URL found",
        "Pappudia Gurkerl Fertiggericht-Fotos": "prepared-meal photos without packaging logo — used OFF Hummus packshot of same brand instead",
        "SPAR enjoy spar.at white-on-transparent": "previously rejected (T12, invisible on light UI) — pack crop on cardboard used instead",
        "interspar.at hd_main/xl_main SPAR enjoy": "HTTP 404; only 180px dt_main available from SPAR CDN for these SKUs",
    },
    "counts": {
        "added": len(added), "updated_fileless": len(updated),
        "total_rows": len(d),
        "with_file": sum(1 for v in d.values() if (v.get("file") or "").strip()),
        "products_impacted_total": sum(impact.values()),
    },
    "sha256": sha,
}
ev = f"{DATEN}/raw/logos_squad_2026-10-13T23.json"
os.makedirs(f"{DATEN}/raw", exist_ok=True)
json.dump(evidence, open(ev, "w"), ensure_ascii=False, indent=1)
print("added", added)
print("updated_fileless", updated)
print("impact", impact)
print("total", len(d), "with_file", evidence["counts"]["with_file"])
for slug in added + updated:
    assert os.path.exists(os.path.join(LOGOS_DIR, d[slug]["file"].split("/",1)[1]))
    assert d[slug]["file"]
print("ok")
