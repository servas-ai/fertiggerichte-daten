"""Daten-Squad 2026-10-16T1736 logo merge: logo long tail (Alfies/MPreis brands).
Vision gate: each final file rendered on white + light grey and inspected via Read (correct brand wordmark, legible,
not a plated-meal/product-hero placeholder). Brand identity cross-checked against the retailer product rows/packshots
and the brand owner's own site (robots checked, no login/JS/cookies). Also adds case/legal-name aliases onto existing
file-backed rows (followfood, frank-juice, knoedelwerkstatt) that strict matching missed."""
import json, shutil, os, datetime, csv, hashlib, collections

G = "Vision gate 2026-10-16T1736 (Daten-Squad): visuell geprüft (korrekte Marke, lesbar, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T1736")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

NEW = [
    ("elfer", "11er (elfer)", ["11er", "elfer", "11er Nahrungsmittel GmbH"], "elfer-11er.svg",
     "https://www.11er.at/fileadmin/files/images/user_upload/01_Startseite/logo-11er-2.svg (11er.at robots: Allow /, Disallow only /typo3/)",
     "Offizielles Oval-Logo '11er elfer AUSTRIA' von 11er.at, unverändert; Betreiber laut Website Galinastraße 34, 6820 Frastanz (Kartoffelprodukte/Rösti = Alfies/MPreis 11er-Rösti-Zeilen)", True, "Markenhersteller"),
    ("ajinomoto", "Ajinomoto", ["Ajinomoto", "AJINOMOTO", "Ajinomoto Oyakata"], "ajinomoto.svg",
     "https://upload.wikimedia.org/wikipedia/commons/c/c1/Ajinomoto_logo.svg (Wikimedia Commons File:Ajinomoto logo.svg, Public domain / textlogo)",
     "Rotes AJINOMOTO-Wordmark (Konzernmarke) von Wikimedia Commons, unverändert; auch für 'Ajinomoto Oyakata'-Zeilen, deren Markenname die Konzernmarke enthält (Oyakata = Ajinomoto-Untermarke; kein eigenes Oyakata-Logo verwendet)", True, "Markenhersteller"),
    ("getvoila", "getvoila", ["Getvoila", "getvoila", "GETVOILA"], "getvoila.svg",
     "https://cdn.shopify.com/s/files/1/0568/3173/8034/files/Logo.svg?v=1713430514 (Header von getvoila.com; robots Disallow nur cart/checkout/search)",
     "Offizielles 'getvoila'-Wordmark von getvoila.com; Original #FAF7F4 (hell auf dunkel) → Füllfarbe #1f1f1f für helle UI, Pfade unverändert; Marke bestätigt über getvoila.com Produkt-Sitemap (neapolitanische-pizza-bufalina/diavola/quattro-formaggi = Alfies 'getvoila … Neapolitanisches Kochkollektiv')", True, "Markenhersteller"),
    ("mamma-emma", "Mamma Emma", ["Mamma Emma", "mamma emma", "MAMMA EMMA"], "mamma-emma.svg",
     "https://www.mammaemma.it/wp-content/uploads/2019/11/logo-brown.svg (mammaemma.it robots: Disallow only cfdb7_uploads)",
     "Offizielles braunes 'mamma emma'-Wordmark von mammaemma.it (Gnocchi di patate), unverändert; = Alfies 'Mamma Emma Kartoffel Gnocchi'-Zeilen", True, "Markenhersteller"),
]

ALIASES = {
    "followfood": ["Followfood", "followfood GmbH"],
    "frank-juice": ["Frank Juice", "FrankJuice GmbH"],
    "knoedelwerkstatt": ["Die Knödelwerkstatt", "Knödelwerkstatt Ges.m.b.H.", "Knödelwerkstatt GmbH"],
}

REJECTED = {
    "Followfish (2 Alfies rows)": "packshot shows the old 'followfish' wordmark; the existing followfood logo has a different wordmark → not aliased (no followfish logo asset on Commons/followfood.de)",
    "followfood.de followfood-logo-2025 SVG": "not needed — existing Commons followfood row kept, only case alias 'Followfood' added",
    "Knödelwerkstatt round logo (Logo_knödelwerkstatt-transparent-web.png)": "existing row already has the official knoedelwerkstatt.at header logo; alias only (Alfies brand 'Knödelwerkstatt Ges.m.b.H.' origin AT = Knödelwerkstatt GmbH, Hauptstraße 12, 4581 Rosenau am Hengstpaß per Impressum; Impressum UID truncated 'ATU' → company not VIES-verified)",
    "The Green Garden / Wiener Virtshaus / Pasta Box / Elsässer": "known rejects from earlier runs — not re-probed",
}

VISION = {
    "elfer": "PASS — yellow oval, red '11er' + black 'elfer' + AUSTRIA (SVG)",
    "ajinomoto": "PASS — red AJINOMOTO wordmark (SVG 1000x139)",
    "getvoila": "PASS — dark 'getvoila' wordmark after recolour (SVG 123x36 viewBox)",
    "mamma-emma": "PASS — brown 'mamma emma' wordmark (SVG)",
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
    w = csv.DictWriter(fh, fields); w.writeheader()
    for r in logos_rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})

bc = collections.Counter()
with open(f"{DATEN}/data/products.csv") as fh:
    for row in csv.DictReader(fh):
        bc[(row.get("brand") or "").strip()] += 1
impact = {slug: sum(bc.get(b, 0) for b in d[slug]["brands"]) for slug in added + updated}

evidence = {
    "run": "2026-10-16T1736 Daten-Squad",
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
ev = f"{DATEN}/raw/logos_squad_2026-10-16T1736.json"
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
