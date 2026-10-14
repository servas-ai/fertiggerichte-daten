"""Daten-Squad 2026-10-14T0006 logo merge: brand-logo long tail (COVERAGE 'Next biggest gap').
Vision gate: each final PNG inspected via Read (correct brand wordmark, legible, not a product/plated-meal photo,
not a placeholder). Sources: official producer site assets (robots checked, plain curl, no login/cookies/JS) or
packshots already in the dataset (Penny commercetools CDN / OFF). Box overloaded -> strictly sequential, no browser."""
import json, shutil, os, datetime, csv, hashlib, collections

G = "Vision gate 2026-10-14T0006 (Daten-Squad): visuell geprüft (korrekte Marke, lesbar, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T0006")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

# slug, name, brands, file, source, origin-note, hq, category
NEW = [
    ("delikatessa", "Delikatessa", ["Delikatessa", "Delikatessa (Penny)"], "delikatessa.png",
     "Penny commercetools packshot (images.cdn.europe-west1.gcp.commercetools.com/787b77ab-…/78-107318-1907479627-eMBE3-2y.jpg, penny.at/produkte/knoedel-78107318, Delikatessa Wurstknödel 10 Stück) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Penny-Eigenmarke Delikatessa (grünes Wordmark mit Swoosh + 'exklusiv bei PENNY.' auf weißem Badge); Quelle 1400x1400, Crop 276x130 ×1.5 + weißer Rand", True, "Eigenmarke"),
    ("rettenswert", "Rettenswert", ["Rettenswert", "Rettenswert von Unverschwendet"], "rettenswert.png",
     "OFF packshot GTIN 4061463369697 front_de.6.full (Rettenswert Curry Bowl Linsen & Mandeln, 2222x4060) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Hofer-Eigenmarke Rettenswert (dunkles Handschrift-Wordmark + 'VON UNVERSCHWENDET' auf hellem Glas-Etikett); Aldi-CDN nicht erneut geprobt (T09 403)", True, "Eigenmarke"),
    ("wolfensberger-pomella", "Wolfensberger & Pomella", ["Wolfensberger & Pomella", "WP Fine Food", "Wolfensberger&Pomella"], "wolfensberger-pomella.png",
     "https://www.wp-finefood.com/img/logowp.png",
     "Offizielles Header-Logo der WP Fine Food GmbH (Kurtatsch, Südtirol; Marke Wolfensberger & Pomella), unverändert 235x88 PNG, weißes Wordmark auf grünem Block; robots.txt 404 (keine Einschränkung), Plain-curl ohne Cookies. Hinweis: die Gurkerl-/MPreis-Packshots tragen das Etikett 'Südtiroler Kochwerk' (eigener Logo-Eintrag suedtiroler-kochwerk), daher offizielles Markenlogo statt Pack-Crop", True, "Markenhersteller"),
    ("schulzis-knoedel", "Schulzi´s Knödel", ["Schulzi´s Knödel", "Schulzi's Knödel", "Schulzi´s", "Schulzi's"], "schulzis-knoedel.png",
     "https://www.brok.at/schulzisknoedel/ (BRoK Catering, Hersteller) — Artikelbild image.jimcdn.com/…/iad700e45d140b2aa/version/1730893318/image.jpg (1005x503) — Ausschnitt Marken-Badge",
     "Ausschnitt des runden Marken-Badges 'SCHULZI'S KNÖDEL · FRISCH · REGIONAL · BRoK.at' aus dem offiziellen Hersteller-Artikelbild (Video-Still); Kreis+Banner-Maske, Hintergrund weiß, ×2 hochskaliert, Wordmark lesbar; robots.txt erlaubt (Crawl-Delay 5 eingehalten); Gurkerl-Packshots zeigen nur Knödel ohne Etikett", True, "Markenhersteller"),
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
        if old.get("note"): entry["note"] += " · vorher (file-less): " + old["note"][:300]
        dest = os.path.join(LOGOS_DIR, fn)
        assert not os.path.exists(dest), "file name collision " + fn
        shutil.copy(sp, dest); d[slug] = entry; updated.append(slug)
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
bc = collections.Counter()
with open(f"{DATEN}/data/products.csv") as fh:
    for row in csv.DictReader(fh):
        bc[(row.get("brand") or "").strip()] += 1
impact = {slug: sum(bc.get(b, 0) for b in d[slug]["brands"]) for slug in added + updated}

evidence = {
    "run": "2026-10-14T0006 Daten-Squad",
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
        "The Green Garden (6 products)": "all 6 Gurkerl images are plated-meal photos (Gurkerl own-label collab) without packaging/logo; no producer site identified — not re-probed (T2340 same result), still open",
        "Wiener Virtshaus (4 products)": "Gurkerl images are plated-meal photos (368x254 plate, no packaging); BS Gastro has no website (T13) — still open",
        "Pasta Box (3 products)": "Gurkerl packshots show open black meal trays without any label; producer Čerstvá pasta – Jan Blažek (Karlovy Vary) has no identifiable official site/logo asset — still open (Sodebo 'PastaBox' is a different French brand, not used)",
        "Elsässer (3 products)": "Gurkerl label reads 'Original frische Elsässer* Quiche … FOOD MAKES FUN' — 'Elsässer' is a product descriptor, not a brand wordmark; brand owner unverified — not cropped",
        "Wolfensberger & Pomella Gurkerl pack crop": "pack label shows 'Südtiroler Kochwerk' (different wordmark, already its own row) — used official wp-finefood.com header logo instead",
        "Delikatessa OFF 9002682104336 front": "400px, no visible Delikatessa logo on the photographed side — used Penny packshot instead",
    },
    "counts": {
        "added": len(added), "updated_fileless": len(updated),
        "total_rows": len(d),
        "with_file": sum(1 for v in d.values() if (v.get("file") or "").strip()),
        "products_impacted_total": sum(impact.values()),
    },
    "sha256": sha,
}
ev = f"{DATEN}/raw/logos_squad_2026-10-14T0006.json"
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
