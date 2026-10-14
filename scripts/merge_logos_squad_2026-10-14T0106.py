"""Daten-Squad 2026-10-14T0106 logo merge: brand-logo long tail (COVERAGE 'Next biggest gap': Therese Mölk + 2-product brands).
Vision gate: each final PNG inspected via Read (correct brand wordmark, legible, not a product/plated-meal photo,
not a placeholder). Sources: official producer site assets (robots checked, plain curl, no login/cookies/JS) or
packshots already in the dataset / on robots-allowed product pages (MPreis Cloudinary, BILLA/Penny commercetools,
Interspar dt_zoom, OFF full-res front, Lidl /p/ page imgproxy rendition). Load low -> sequential, no browser."""
import json, shutil, os, datetime, csv, hashlib, collections

G = "Vision gate 2026-10-14T0106 (Daten-Squad): visuell geprüft (korrekte Marke, lesbar, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T0106")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"
CL = "https://res.cloudinary.com/dit8huoga/image/upload"
BI = "https://images.cdn.europe-west1.gcp.commercetools.com/723b2575-66c7-4d92-ae49-82bf1d168d26"
PE = "https://images.cdn.europe-west1.gcp.commercetools.com/787b77ab-692c-4e25-91f4-697690dc3c7c"

# slug, name, brands, file, source, origin-note, hq, category
NEW = [
    ("therese-moelk", "Therese Mölk", ["Therese Mölk", "Bäckerei Therese Mölk", "THERESE MÖLK"], "therese-moelk.png",
     f"{CL}/v1768288563/api/custom/844735_front.jpg (MPreis Packshot Therese Mölk Himbeerknödel 4er, EAN 9005015055459, 2480x2437) — Ausschnitt Marken-Badge",
     "Packshot-Ausschnitt MPreis-Bäckereimarke Therese Mölk (Strichzeichnung Gesicht + 'THERESE MÖLK · Purer Genuss.' aus dem gezackten Badge); Badge-Hintergrund auf Weiß normalisiert, Tinte dunkel, Zackenrand entfernt. Offizielle Seite therese-moelk.at leitet auf mpreis.at/vielfalt/unsere-marken/baeckerei-therese-moelk (robots Allow /) — dort nur Foto-Header-Banner, kein freigestelltes Logo; theresemoelk.at TLS EOF (nicht umgangen)", True, "Eigenmarke"),
    ("ager", "Ager", ["Ager", "AGER", "Qualität Ager"], "ager.png",
     f"{BI}/00-730656-0432126918-r8rI-sGc.jpg (BILLA Packshot Ager Rehragout geschnitten, 1200x1309) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt ovales Markenlogo 'QUALITÄT AGER' (rot/weiß/blau) vom Etikett; Quelle klein (~130 px), 16° gerade gedreht, ×4 Lanczos, Ellipsen-Maske auf Weiß (Bergfoto/Fahnenstreifen entfernt) — weich, aber lesbar. ager.cc Header-Logo ist Icon-Font (T13), daher Pack-Crop", True, "Markenhersteller"),
    ("tann", "TANN", ["TANN", "Tann", "TANN (Spar)"], "tann.png",
     "https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/2020000772651/dt_zoom.jpg (Interspar Packshot TANN Cevapcici, 1001x1001) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt SPAR-Eigenmarke TANN (rotes Oval, weißes Wordmark, mintgrüner Swoosh) vom Etikettband 'WENN GENUSS … VON SPAR'; Quelle ~140 px, ×4 Lanczos, Taupe-Band per Flood-Fill auf Weiß — weich, aber lesbar. spar.at/eigenmarken/lebensmittel liefert Cloudflare-Challenge (nicht umgangen)", True, "Eigenmarke"),
    ("njami", "Njami", ["Njami", "NJAMI", "Njami by Delamaris"], "njami.png",
     f"{BI}/00-885825-438096192-9NY20Ilx.jpg (BILLA Packshot Njami Chicken Bowl Mexicana, 3277x3277) — Ausschnitt Marken-Lockup",
     "Packshot-Ausschnitt 'NJAMI' (rotes Wordmark auf rosa) + 'BY Delamaris · 1879'-Badge, unverändert bis auf Zuschnitt/Verkleinerung 800 px; Vertrieb AT Glatz GmbH", True, "Markenhersteller"),
    ("pizz-ah", "PIZZ'AH", ["PIZZ'AH", "PIZZ’AH", "Pizz'ah"], "pizz-ah.png",
     "OFF packshot GTIN 4061463587275 front_de.17.full (PIZZ'AH Steinofenpizza Diavola, 2560x2544) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Hofer-Eigenmarke PIZZ'AH (schwarzes Wordmark mit Pizzastück-A auf cremefarbenem Badge); Badge per Farbmaske freigestellt, Holz/Karo-Hintergrund auf Weiß. Aldi-CDN nicht erneut geprobt (T09 403)", True, "Eigenmarke"),
    ("leibspeis", "Leibspeis'", ["Leibspeis'", "Leibspeis", "Leibspeis’"], "leibspeis.png",
     "OFF packshot GTIN 4099200227771 front_de.3.full (Leibspeis' Tomaten-Mozzarella-Nudeln, 2281x3751) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Hofer-Eigenmarke Leibspeis' (schwarzes Schreibschrift-Wordmark + Swoosh + rot-weiß-rote Fahne 'IN ÖSTERREICH G'MACHT'); grauer Holz-Hintergrund per Flat-Field auf Weiß, Karotuch-Ecke entfernt", True, "Eigenmarke"),
    ("mcennedy", "MCENNEDY", ["MCENNEDY", "McEnnedy", "Mcennedy"], "mcennedy.png",
     "https://www.lidl.at/p/mcennedy-nudelauflauf-mac-cheese/p10056595 (robots: /p/ erlaubt) — imgproxy-retcat.assets.schwarz …/w:1500/h:1125/… (Packshot Nudelauflauf Mac & Cheese) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Lidl-Eigenmarke MCENNEDY 'AMERICAN WAY' (weißes Schild, navy/rote Umrandung, 5 Sterne); rotes Pack-Umfeld per Flood-Fill auf Weiß, ×2 Lanczos. Nur die vom Produktseiten-HTML referenzierte signierte 1500er-Rendition geladen (keine API, kein /q/api)", True, "Eigenmarke"),
    ("staudinger", "Staudinger", ["Staudinger", "Staudinger's", "STAUDINGER'S", "Staudinger´s"], "staudinger.png",
     f"{BI}/00-698017-707306118-J1-9R-AF.jpg (BILLA Packshot Staudinger Holzofen Leberkäs geschnitten, 1600x1600) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt goldener Bogen 'STAUDINGER'S' + 'HOLZOFEN SPEZIALITÄTEN' auf rotem Etikett; Leberkäse-Foto oberhalb des Bogens per Kreisbogen-Maske auf Weiß, ×2 Lanczos. staudinger-delikatessen.at TLS EOF / holzofen-leberkaes.at Zertifikat-Hostname-Mismatch (nicht umgangen)", True, "Markenhersteller"),
    ("exotic-food", "Exotic Food", ["Exotic Food", "EXOTIC FOOD", "Exotic Food Thailand"], "exotic-food.png",
     "https://www.exoticfoodthailand.com/wp-content/uploads/2020/08/Exotic-Logo-1.png",
     "Offizielles Logo von exoticfoodthailand.com (Exotic Food Thailand; Site-Icon-Original 'cropped-Exotic-Logo-1' als 707x707 PNG mit Transparenz, unverändert): 'Exotic Food'-Schild mit Chili + 'AUTHENTIC THAI'-Banner + 'Thailand On a Plate!'; identisch mit dem Etikett-Badge auf der MPreis-Dose Tom Yum (EAN 8853662002019); robots.txt erlaubt (nur /wp-admin/), Plain-curl", True, "Markenhersteller"),
    ("taste-of-asia", "Taste Of Asia", ["Taste Of Asia", "Taste of Asia", "TASTE OF ASIA"], "taste-of-asia.png",
     f"{PE}/78-267102-427881130-amxyBx8i.jpg (Penny Packshot Taste of Asia Mini-Frühlingsrollen, 1400x1400) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Penny-Marke 'Taste of ASIA' (weißes Wordmark auf rotem Feld mit orange Asien-Karte), unverändert bis auf Zuschnitt, ×2 Lanczos", True, "Eigenmarke"),
    ("fryzza", "Fryzza", ["Fryzza", "FRYZZA"], "fryzza.png",
     f"{CL}/v1781744491/api/813756_angle.jpg (MPreis Packshot Fryzza Salami Pizza, EAN 4262548740046, 1333x1333) — Ausschnitt Wordmark",
     "Packshot-Ausschnitt 'FRY/ZZA'-Wordmark (weiß auf rotem Feld) von der Packungsfront, unverändert bis auf Zuschnitt", True, "Markenhersteller"),
    ("schenkel", "Schenkel", ["Schenkel", "SCHENKEL"], "schenkel.png",
     f"{CL}/v1779619454/api/187011_angle.jpg (MPreis Packshot Schenkel Hummerrahmsuppe, EAN 4003011240522, 10439x11585) — Ausschnitt Wordmark-Band",
     "Packshot-Ausschnitt 'SCHENKEL'-Wordmark (weiß auf violettem Band mit Goldkanten) vom Glas-Etikett, unverändert bis auf Zuschnitt/Verkleinerung 900 px", True, "Markenhersteller"),
]
# brand aliases onto existing file-backed rows (same brand, spelling variant in products.csv)
ALIASES = {"nature-s-gold": ["Nature‘s Gold"], "wech": ["Wech", "WECH"]}

REJECTED = {
    "The Green Garden / Wiener Virtshaus / Pasta Box / Elsässer": "known dead ends from T0006 (plated-meal photos only / unlabelled trays / descriptor not wordmark) — not re-probed this run",
    "SPAR Asia (2 products)": "Interspar dt_zoom packshot (Shrimp Suppe Yellow Curry) shows only the SPAR logo + product name + 'Taste of Thailand' sticker, no 'SPAR ASIA' wordmark; not aliased to Spar (sub-brand ≠ chain logo)",
    "Vifon (2 products)": "unchanged from T18: producer of MPreis VIFON packs (5901882… = Polish GS1, Tan-Viet/Vifon Europe) unverified vs. vifon.com.vn — no images in dataset",
    "Go (2 products, Unimarkt)": "no packshot in dataset, brand string 'Go' too generic to verify",
    "Asia (2 products, Hofer/OFF)": "generic descriptor ('Asia' Hofer Asia-Linie), not a verifiable wordmark",
    "Exotic Food pack crop": "badge on can overlapped by 'AUTHENTIC THAI' ribbon; a flat-black masking attempt was discarded — used the official exoticfoodthailand.com logo instead",
    "Leibspeis' crop v1": "first crop cut the wordmark (wrong preview scale) — redone from full-res OFF front",
    "Spar Eigenmarken page (TANN)": "spar.at/eigenmarken/lebensmittel returned a Cloudflare 'Just a moment' challenge — not bypassed; TANN cropped from Interspar packshot instead",
    "Therese Mölk official page": "mpreis.at brand page (robots Allow /) has only photo header banners (csm_mpr_header-banner_…jpg) and the generic MPreis og-image — no standalone Therese Mölk logo asset; theresemoelk.at TLS EOF",
}
VISION = {
    "therese-moelk": "PASS — line-drawing face + 'THERESE MÖLK / Purer Genuss.' crisp black on white (471x462)",
    "ager": "PASS (soft) — oval 'QUALITÄT AGER' red/blue legible, low-res source upscaled (584x380)",
    "tann": "PASS (soft) — red oval 'TANN' with mint swoosh legible, low-res source upscaled (545x263)",
    "njami": "PASS — big red 'NJAMI' + purple 'BY Delamaris 1879' badge on pink (800x484)",
    "pizz-ah": "PASS — black 'PIZZ'AH' with pizza-slice A on cream badge, white surround (775x513)",
    "leibspeis": "PASS — black script 'Leibspeis'' + swoosh + red-white-red flag, white background (844x349)",
    "mcennedy": "PASS — 'MCENNEDY AMERICAN WAY' shield with 5 stars, crisp (766x378)",
    "staudinger": "PASS — gold arch 'STAUDINGER'S' + 'HOLZOFEN SPEZIALITÄTEN' on red, meat photo removed (880x392)",
    "exotic-food": "PASS — official lockup, transparent PNG renders on white (707x707)",
    "taste-of-asia": "PASS — white 'Taste of ASIA' on red with orange Asia map (724x396)",
    "fryzza": "PASS — white 'FRY ZZA' stacked wordmark on red (362x362)",
    "schenkel": "PASS — white 'SCHENKEL' on violet band with gold edges (900x188)",
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

# product impact
bc = collections.Counter()
with open(f"{DATEN}/data/products.csv") as fh:
    for row in csv.DictReader(fh):
        bc[(row.get("brand") or "").strip()] += 1
impact = {slug: sum(bc.get(b, 0) for b in d[slug]["brands"]) for slug in added + updated}

evidence = {
    "run": "2026-10-14T0106 Daten-Squad",
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
ev = f"{DATEN}/raw/logos_squad_2026-10-14T0106.json"
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
