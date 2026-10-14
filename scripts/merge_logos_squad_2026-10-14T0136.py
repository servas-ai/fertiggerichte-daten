"""Daten-Squad 2026-10-14T0136 logo merge: single-product logo-less long tail after T0106.
Vision gate: each final PNG inspected via Read (correct brand wordmark, legible, not a plated-meal/product-hero
placeholder). Sources: packshots already in the dataset / robots-allowed product pages (OFF full-res, MPreis
Cloudinary, BILLA/Penny commercetools, Interspar dt_zoom, Lidl imgproxy small, dm-static, Gurkerl CDN) or
official producer site assets (henglein.de, rebel-meat.com — robots Allow). Load low -> sequential."""
import json, shutil, os, datetime, csv, hashlib, collections

G = "Vision gate 2026-10-14T0136 (Daten-Squad): visuell geprüft (korrekte Marke, lesbar, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T0136")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"
CL = "https://res.cloudinary.com/dit8huoga/image/upload"
BI = "https://images.cdn.europe-west1.gcp.commercetools.com/723b2575-66c7-4d92-ae49-82bf1d168d26"
PE = "https://images.cdn.europe-west1.gcp.commercetools.com/787b77ab-692c-4e25-91f4-697690dc3c7c"
OFF = "https://images.openfoodfacts.org/images/products"

# slug, name, brands, file, source, origin-note, hq, category
NEW = [
    ("henglein", "Henglein", ["Henglein", "HENGLEIN"], "henglein.png",
     "https://www.henglein.de/wp-content/uploads/2024/01/Henglein_Logo_waagrecht.svg (robots Allow /; Disallow only wpo-plugins-tables-list.json)",
     "Offizielles Logo von henglein.de (SVG→PNG via cairosvg, schwarze Flächen auf Weiß, Slogan 'Schmeckt wie selbstgemacht' belassen); bestätigt gegen MPreis Packshot Schupfnudeln EAN 4001163000599", True, "Markenhersteller"),
    ("rebel-meat", "Rebel Meat", ["Rebel Meat", "REBEL MEAT", "Rebel Kids"], "rebel-meat.png",
     "https://static.wixstatic.com/media/5d34d3_050cf047bf554c238092f01e9eede5a4~mv2.png (rebel-meat.com robots Allow /)",
     "Offizielles Wordmark von rebel-meat.com (Wix CDN, Voll-PNG ohne Fill-Transform): 'Rebel' Brush-Script + 'MEAT' Block; Weiß-auf-Schwarz → Schwarz-auf-Weiß für UI; bestätigt gegen BILLA Packshot Rebel Kids Bio Hühner-Nuggets", True, "Markenhersteller"),
    ("just-veg", "Just Veg!", ["Just Veg!", "Just Veg", "JUST VEG!"], "just-veg.png",
     f"{OFF}/406/146/301/2364/front_en.4.full.jpg (OFF Pizza Toona, GTIN 4061463012364) — Ausschnitt Marken-Badge",
     "Packshot-Ausschnitt limettengrünes Schild 'Just Veg!' (dunkelgrünes Wordmark) auf Blattadern-Hintergrund; unverändert bis auf Zuschnitt", True, "Markenhersteller"),
    ("findus", "Findus", ["Findus", "FINDUS"], "findus.png",
     f"{OFF}/905/481/822/5323/front_en.3.full.jpg (OFF Zuppa del Casale) — Ausschnitt rotes Findus-Banner",
     "Packshot-Ausschnitt klassisches Findus-Flaggenlogo (weiß auf rot) vom TK-Beutel; Quelle niedrigauflösend, ×Lanczos — weich, aber lesbar", True, "Markenhersteller"),
    ("diamond", "Diamond", ["Diamond", "DIAMOND"], "diamond.png",
     "https://cdn.gurkerl.at/images/grocery/products/31821/31821-1704787131028.jpg (Gurkerl Mini-Frühlingsrollen Tsingtao) — Ausschnitt Markenbanner",
     "Packshot-Ausschnitt rotes Banner 'Diamond' (weiße Schreibschrift, Goldkante) auf dunkelgrünem Karton", True, "Markenhersteller"),
    ("lorado", "Lorado", ["Lorado", "LORADO"], "lorado.png",
     "https://www.interspar.at/media/a5/37/b5/1789340689/A_2020004338648_HB.jpg (Interspar Lorado Ravioli) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt rotes Blatt-Banner 'Lorado' / 'Qualität' auf grüner Dose; Dose-Rand teilweise sichtbar", True, "Eigenmarke"),
    ("schwaben-krone", "Schwaben Krone", ["Schwaben Krone", "SchwabenKrone", "SCHWABEN KRONE"], "schwaben-krone.png",
     f"{OFF}/407/560/039/8891/front_de.8.full.jpg (OFF Wildmaultaschen) — Ausschnitt Markenband",
     "Packshot-Ausschnitt tealgrünes Band mit Kronen-Icon + weißem Script 'SchwabenKrone'; Produktname darunter entfernt", True, "Markenhersteller"),
    ("harvest-moon", "Harvest Moon", ["Harvest Moon", "HARVEST MOON", "Harvest"], "harvest-moon.png",
     f"{BI}/00-876568-162362339-AUslsecq.jpg (BILLA Harvest Moon Chocolate & salted Caramel) — Ausschnitt Mond-Badge",
     "Packshot-Ausschnitt weißes Mond-Kreis-Badge 'HARVEST MOON' (schwarz gestapelt) auf mahagonifarbenem Sleeve", True, "Markenhersteller"),
    ("yopokki", "Yopokki", ["Yopokki", "YOPOKKI", "요뽀끼"], "yopokki.png",
     "https://cdn.gurkerl.at/images/grocery/products/38273/38273-1738164067006.jpg (Gurkerl Instant Topokki Kimchi) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt zentrales YOPOKKI-Lockup (roter Topf-Outline + koreanisch + lateinisch); Young-Poong-Parent-Badge nicht als eigener Brand-Eintrag", True, "Markenhersteller"),
    ("vitasia", "Vitasia", ["Vitasia", "VITASIA"], "vitasia.png",
     f"{OFF}/433/561/912/7579/front_en.11.full.jpg (OFF Lentil and Chickpea Curry) — Ausschnitt Markenbanner",
     "Packshot-Ausschnitt lila Lidl-Asia-Banner 'VITASIA' + Pagoden-Icon + 'INDIAN STYLE' vom Dosenetikett", True, "Eigenmarke"),
    ("pan", "Pan", ["Pan", "PAN", "Pan Südtiroler"], "pan.png",
     f"{CL}/v1768841982/api/803545_angle.jpg (MPreis Pan Südtiroler Topfenstrudel, EAN 8000460011174) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt rotes Squircle 'Pan' (weiße Schreibschrift) auf Holzmaserung", True, "Markenhersteller"),
    ("flotte-lotte", "Flotte Lotte", ["Flotte Lotte", "FLOTTE LOTTE"], "flotte-lotte.png",
     f"{OFF}/912/011/349/1784/front_de.8.full.jpg (OFF Fenchel Kartoffel Suppe) — Ausschnitt Wordmark",
     "Packshot-Ausschnitt 'FLOTTE LOTTE' (O als Apfel mit Blatt) + Slogan-Zeile vom Glas-Etikett", True, "Markenhersteller"),
    ("spar-bbq", "SPAR BBQ", ["SPAR BBQ", "Spar BBQ", "SPAR BBQ Grill"], "spar-bbq.png",
     "https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/2020001842452/dt_zoom.jpg (Interspar Grill-Gemüse-Trilogie) — Ausschnitt Sub-Brand-Lockup",
     "Packshot-Ausschnitt eigenständiges Sub-Brand-Lockup 'BBQ' (weißes Sketch-Wordmark) + SPAR-Logo auf schwarzem Beutel — nicht nur Kettenlogo", True, "Eigenmarke"),
    ("thai-delight", "Thai Delight", ["Thai Delight", "THAI DELIGHT"], "thai-delight.png",
     "https://cdn.gurkerl.at/images/grocery/products/38498/38498-1738673865144.jpg (Gurkerl Hokkien Noodles) — Ausschnitt Marken-Crest",
     "Packshot-Ausschnitt cremefarbener Thai-Delight-Crest (Elefant-Icon + Wordmark) vom Karton", True, "Markenhersteller"),
    ("dozz", "Dozz", ["Dozz", "DOZZ"], "dozz.png",
     f"{CL}/v1783731750/api/585631_angle.png (MPreis Dozz Spinatsuppe, EAN 5941905400814) — Ausschnitt Wordmark",
     "Packshot-Ausschnitt weißes 'DOZZ'-Serif-Wordmark auf mintgrünem Dosenband", True, "Markenhersteller"),
    ("hildegard-gruenkraft", "Hildegard Grünkraft", ["Hildegard Grünkraft", "HILDEGARD GRÜNKRAFT"], "hildegard-gruenkraft.png",
     "https://products.dm-static.com/images/f_auto,q_auto,c_fit,h_1200,w_1200/v1747539433/assets/pas/images/2575ab79-d644-46e2-8cd4-3bb91c86a091/hildegard-gruenkraft-suppe-bio-fasten (dm Bio Fasten Suppe) — Ausschnitt Marken-Badge",
     "Packshot-Ausschnitt dunkelgrünes Badge 'HILDEGARD GRÜNKRAFT' + Hildegard-Profilillustration vom Becher", True, "Markenhersteller"),
    ("deliciosu", "Deliciosu", ["Deliciosu", "DELICIOSU"], "deliciosu.png",
     f"{BI}/00-763125-0195716755-SCIoaKQJ.jpg (BILLA Deliciosu Poké Bowl Lachs) — Ausschnitt Deckel-Logo",
     "Packshot-Ausschnitt rundes Deckel-Logo 'Deliciosu' (weiß serif auf blau, Hummer-Icon)", True, "Markenhersteller"),
    ("deluxe", "Deluxe", ["Deluxe", "DELUXE"], "deluxe.png",
     f"{OFF}/000/002/015/9689/front_de.14.full.jpg (OFF Medaglioni Mushrooms & Truffle) — Ausschnitt Wordmark-Band",
     "Packshot-Ausschnitt schwarzes Band mit weißem Kursiv-Wordmark 'Deluxe' + hellblauem Swoosh (Lidl Premium)", True, "Eigenmarke"),
    ("auinger", "Auinger", ["Auinger", "AUINGER"], "auinger.png",
     f"{OFF}/912/000/449/0049/front_de.4.full.jpg (OFF Klare Suppe) — Ausschnitt Oval-Badge",
     "Packshot-Ausschnitt gelbes Oval 'Auinger' (grüne Schreibschrift, roter Schatten, Weiß/Schwarz-Rand)", True, "Markenhersteller"),
    ("alpenstrudel", "Alpenstrudel", ["Alpenstrudel", "Alpen Strudel", "Alpenstrudel delle Alpi"], "alpenstrudel.png",
     f"{CL}/v1768841976/api/813093_angle.jpg (MPreis Südtiroler Apfelstrudel, EAN 8000460010207) — Ausschnitt Wordmark",
     "Packshot-Ausschnitt 'Alpen' + Script 'Strudel' + Berg-Icon + 'delle Alpi' auf Jute-Hintergrund", True, "Markenhersteller"),
    ("sushitime", "Sushitime", ["Sushitime", "sushitime", "Sushi Time"], "sushitime.png",
     f"{BI}/00-731600-0165537535-Dts1bHw3.jpg (BILLA Lachs Picknick) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt 'sushi'(schwarz)+'time'(rot) mit Chopstick/Sushi-Kreis-Icon auf hellgrünem Muster", True, "Markenhersteller"),
    ("ich-bin-oesterreich", "Ich bin Österreich", ["Ich bin Österreich", "Ich bin ÖSTERREICH"], "ich-bin-oesterreich.png",
     f"{PE}/78-790129-2110285495-Yqixh0-3.jpg (Penny Wiener Schnitzel) — Ausschnitt Holzschild-Badge",
     "Packshot-Ausschnitt Holzschild 'Ich bin / ÖSTERREICH' mit Österreich-Flaggenband auf orange", True, "Eigenmarke"),
    ("muehlen", "Mühlen", ["Mühlen", "Rügenwalder Mühle", "Rügenwalder", "Ruegenwalder Mühle"], "muehlen.png",
     f"{BI}/00-323146-1399185890-gMYl8TcU.jpg (BILLA Vegane Mühlen Cordon Bleu) — Ausschnitt Windmühlen-Icon + Wordmark",
     "Packshot-Ausschnitt Rügenwalder-Mühle-Icon (Wurst-Flügel, 1834) + weißes 'MÜHLEN'-Wordmark; Brand in products.csv = 'Mühlen'", True, "Markenhersteller"),
    ("big-snack", "Big Snack", ["Big Snack", "BIG SNACK"], "big-snack.png",
     f"{CL}/v1779633301/api/80368_angle.jpg (MPreis Cheeseburger 2er, EAN 9002931030737) — Ausschnitt Markenbadge",
     "Packshot-Ausschnitt 'Big Snack'-Badge (rote Schreibschrift in weißem Wolken-Oval + Liberty-Emblem)", True, "Markenhersteller"),
    ("ocean-sea", "Ocean Sea", ["Ocean Sea", "OCEAN SEA", "ocean sea"], "ocean-sea.png",
     "Lidl imgproxy 427×320 Fish & Chips packshot (products.csv image_url; größere /w:1500 Rendition 403 — nicht umgangen) — Ausschnitt rotes Kreislogo",
     "Packshot-Ausschnitt rotes Kreislogo 'ocean sea' + Fisch-Icon; Quelle klein, ×Lanczos — weich, aber lesbar", True, "Eigenmarke"),
    ("franui", "franuí", ["franuí", "franui", "Franui"], "franui.png",
     f"{BI}/00-895905-0112815057-XPoOinJA.jpg (BILLA franuí Raspberry) — Ausschnitt Deckel-Wordmark",
     "Packshot-Ausschnitt Deckel-Wordmark 'franuí' (dunkles Rot auf dusty-rose) + 'RECIPE FROM PATAGONIA' / 'PINK'", True, "Markenhersteller"),
    ("arteoliva", "Arteoliva", ["Arteoliva", "ARTEOLIVA"], "arteoliva.png",
     f"{CL}/v1779630025/api/186837_angle.jpg (MPreis Arteoliva Gazpacho Andaluz, EAN 8437001133147) — Ausschnitt Markenlockup",
     "Packshot-Ausschnitt Kreis-'A' + 'ARTEOLIVA' + Slogan 'arte en la cocina'; arteoliva.com robots Disallow: / für * — daher Pack-Crop", True, "Markenhersteller"),
    ("penny-ready", "Penny Ready", ["Penny Ready", "PENNY READY", "PennyReady"], "penny-ready.png",
     f"{OFF}/433/725/637/2008/front_de.6.full.jpg (OFF Lasagne alla Bolognese) — Ausschnitt Wordmark",
     "Packshot-Ausschnitt blaues 'PENNY READY'-Wordmark auf Kartontextur; leicht angeschnitten, aber lesbar", True, "Eigenmarke"),
]

# aliases onto existing file-backed rows
ALIASES = {
    # SchwabenKrone spelling already included in NEW brands; no extra existing slug needed
}

REJECTED = {
    "The Green Garden / Wiener Virtshaus / Pasta Box / Elsässer / Asia / Vifon / SPAR Asia / Go": "known dead ends from T0006/T0106 — not re-probed",
    "El Tequito": "OFF Chili-con-carne packshot shows Kania oval wordmark, not El Tequito — crop discarded (Kania already file-backed)",
    "Gabelkönig": "Penny packshot only shows 'Supaaa! Günstig.' promo badge; no Gabelkönig wordmark visible",
    "Windisch": "Gurkerl pack shows large serif 'W' + product name 'Kalbs Butter Schnitzel' but no 'Windisch' wordmark — too incomplete",
    "Natur Aktiv / Aldi, Natur Aktiv": "OFF packshot crop regions only showed V-Label vegan seal + food hero; Natur-Aktiv leaf wordmark not isolatable in available front image",
    "Bio Natura": "OFF Steinpilz-Risotto pouch: corner scans showed brown pouch texture / no isolatable Bio-Natura leaf wordmark",
    "innocent": "OFF bottle crop only captured partial halo-face / 'neu' sticker; full innocent wordmark not in frame",
    "SPAR Free From": "Interspar zoom crop cut the 'free from' script mid-word; SPAR tree present but incomplete sub-brand mark — rejected rather than alias to SPAR",
    "Holzbauer": "Interspar dt_zoom is plated spare-ribs hero only — no packaging wordmark",
    "INTERSPAR (Backstube)": "Interspar dt_zoom is food-hero only — no distinct INTERSPAR Backstube wordmark",
    "GOLDEN / My Vay / SELECT&GO": "no usable packshot (empty image_url) or Lidl imgproxy larger rendition 403 (signed URL only from HTML — not scraped beyond robots-allowed small asset)",
    "SOTO": "images.dennree.de fitinto URL 404",
    "Arteoliva official site": "arteoliva.com robots.txt User-agent: * Disallow: / — not fetched; used MPreis pack crop instead",
    "Findus / Innocent Wikimedia": "commons search returned 0 hits; pack/official used instead",
}

VISION = {
    "henglein": "PASS — official blue HENGLEIN + red slogan on white (900x227)",
    "rebel-meat": "PASS — official Rebel brush + MEAT block, black on white (900x622)",
    "just-veg": "PASS — Just Veg! shield wordmark on leaf pack (900x408)",
    "findus": "PASS (soft) — red Findus flag, low-res upscaled (900x416)",
    "diamond": "PASS — white Diamond script on red gold-edged banner (900x357)",
    "lorado": "PASS — Lorado Qualität red leaf badge on green can (900x470)",
    "schwaben-krone": "PASS — crown + SchwabenKrone script on teal band (900x292)",
    "harvest-moon": "PASS — HARVEST MOON in white moon circle (895x520)",
    "yopokki": "PASS — YOPOKKI lockup with pot outline (900x613)",
    "vitasia": "PASS — VITASIA + pagoda on purple Lidl banner (900x442)",
    "pan": "PASS — white Pan script in red squircle (900x488)",
    "flotte-lotte": "PASS — FLOTTE LOTTE with apple-O (900x323)",
    "spar-bbq": "PASS — BBQ sketch wordmark + SPAR logo on black (900x385)",
    "thai-delight": "PASS — Thai Delight crest with elephant (900x431)",
    "dozz": "PASS — white DOZZ serif on mint band (840x510)",
    "hildegard-gruenkraft": "PASS — HILDEGARD GRÜNKRAFT + portrait badge (575x432)",
    "deliciosu": "PASS — Deliciosu round lid logo (900x377)",
    "deluxe": "PASS — white Deluxe script on black band (900x180)",
    "auinger": "PASS — Auinger oval badge green/red on yellow (900x408)",
    "alpenstrudel": "PASS — Alpen + Strudel script + mountain icon (900x322)",
    "sushitime": "PASS — sushitime wordmark + chopstick icon (900x258)",
    "ich-bin-oesterreich": "PASS — wooden Ich bin ÖSTERREICH sign (900x313)",
    "muehlen": "PASS — Rügenwalder windmill + MÜHLEN wordmark (576x436)",
    "big-snack": "PASS — Big Snack cloud badge (900x336)",
    "ocean-sea": "PASS (soft) — ocean sea red circle, low-res upscaled (768x640)",
    "franui": "PASS — franuí lid wordmark dusty-rose (900x272)",
    "arteoliva": "PASS — A circle + ARTEOLIVA + slogan (900x771)",
    "penny-ready": "PASS (soft) — PENNY READY blue wordmark, slightly cropped (900x672)",
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
    "run": "2026-10-14T0136 Daten-Squad",
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
ev = f"{DATEN}/raw/logos_squad_2026-10-14T0136.json"
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
