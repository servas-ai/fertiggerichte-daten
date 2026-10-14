"""Daten-Squad 2026-10-14T0404 logo merge: logo long tail after the Little Lunch dead end (own shop closed 30.09.2025).
Vision gate: each final file rendered on white + dark and inspected via Read (correct brand wordmark, legible,
not a plated-meal/product-hero placeholder). Sources: official producer sites (robots checked, no login/JS/cookies;
entity cross-checked against the producer address in products.csv / Impressum) and Wikimedia Commons (Public domain text logo)."""
import json, shutil, os, datetime, csv, hashlib, collections

G = "Vision gate 2026-10-14T0404 (Daten-Squad): visuell geprüft (korrekte Marke, lesbar, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T0404")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

# slug, name, brands, file, source, origin-note, hq, category
NEW = [
    ("yuun-mee", "Yuu'n Mee", ["Yuu'n Mee", "Yuu'n mee", "Yuu´n Mee", "Yuu’n Mee", "YUU'N MEE", "Yuu'n Mee fine foods Vertriebs-GmbH"], "yuun-mee.svg",
     "https://www.yuu-n-mee.at/wp-content/themes/ynm-theme/Logo_YNM_0109_V4.svg (yuu-n-mee.at robots: Disallow only /wp-admin/)",
     "Offizielles Header-Logo-SVG von yuu-n-mee.at, unverändert: rote Karte mit weißem 'YUU'N MEE'-Wordmark (grünes 'n') + Slogan 'finest Seafood – enjoy the Difference'; Betreiber Yuu'n Mee fine foods Vertriebs-GmbH, McDonald's Strasse 4, 2100 Korneuburg = Producer in products.csv", True, "Markenhersteller"),
    ("allgroo", "Allgroo", ["Allgroo", "allgroo", "ALLGROO"], "allgroo.png",
     "https://static.wixstatic.com/media/447e6e_dc2ee3d31ba94898956a184b37dd622b~mv2.png (allgroo_logo_2.png, Header von allgroo.com; robots Allow /)",
     "Offizielles rotes 'allgroo'-Wordmark (Blatt + Smile) von allgroo.com, nur transparenter Rand beschnitten; allgroo.com Kontakt nennt 56-34 Simyo-gil, Namwon-si, Jeollabuk-do = GMF Co., Ltd. (Producer in products.csv)", True, "Markenhersteller"),
    ("bedford", "Bedford", ["Bedford", "BEDFORD", "Bedford GmbH + Co. KG"], "bedford.png",
     "https://bedford.de/wp-content/uploads/2018/06/bf_logo_white.png (Header von bedford.de; robots Disallow nur wc-logs/transients/add-to-cart/wp-admin)",
     "Offizielles Bedford-Script-Logo + Swoosh + 'Delikat essen' von bedford.de; Original weiß-auf-transparent → Füllfarbe #1f1f1f für helle UI (Alpha unverändert); Impressum Bedford GmbH + Co. KG, Traiteur-Platz 1, 49090 Osnabrück, HRA 2736 AG Osnabrück = Producer in products.csv", True, "Markenhersteller"),
    ("costa", "Costa", ["Costa", "COSTA", "COSTA Meeresspezialitäten"], "costa.png",
     "https://www.costa.de/_assets/639468b5d67b471e16952a11b4231513/Standard/Images/Footer/footer_logo_costa.png (costa.de robots Allow /)",
     "Offizielles 'COSTA'-Wordmark (blau, Garnele im O) auf weißem Pinselstrich aus dem costa.de-Footer, unverändert (304×121, klein aber scharf); Impressum COSTA Meeresspezialitäten GmbH & Co. KG, Stedinger Strasse 25, 26723 Emden, HRA 100513 AG Aurich, USt-ID DE214671468 = Producer in products.csv", True, "Markenhersteller"),
    ("beyond-meat", "Beyond Meat", ["Beyond Meat", "BEYOND MEAT", "Beyond Meat EU B.V."], "beyond-meat.svg",
     "https://upload.wikimedia.org/wikipedia/commons/0/0f/Beyond_Meat_2022_logo.svg (Wikimedia Commons File:Beyond Meat 2022 logo.svg, Public domain / textlogo)",
     "Beyond-Meat-Wordmark 2022 (schwarz) von Wikimedia Commons, unverändert; Lizenz laut Commons: Public domain (Text-Logo)", True, "Markenhersteller"),
]

ALIASES = {}

REJECTED = {
    "Little Lunch (online provider)": "own littlelunch.com shop closed 30.09.2025 ('Shop zu und nu?'); product pages only link to DE retailers Amazon/Flink/Picnic/Rewe/Rossmann — no own sale/AT delivery; existing little-lunch logo row unchanged",
    "Yuu'n Mee YuunMee_Logo_Loader.png": "loader animation frame — the header SVG is used instead",
    "Allgroo ALLGROO_LOGOS.png": "multi-brand strip (allgroo classics / 한국밥상 / hangroo / みんなの和食) — single allgroo wordmark used instead",
    "Bedford B_logo.png": "101×64 monogram 'B' only — full wordmark used instead",
    "Costa costa-garnele.svg": "decoration shrimp icon only, no wordmark",
    "Pierre Baguette": "pierrebaguette.sk homepage exposes only banner/product images (no logo asset URL; logo inline in SPA) — not scraped further, deferred",
    "The Green Garden / Wiener Virtshaus / Pasta Box / Elsässer": "known rejects from earlier runs — not re-probed",
}

VISION = {
    "yuun-mee": "PASS — official red card, white YUU'N MEE wordmark + slogan (SVG 869x521 viewBox)",
    "allgroo": "PASS — red allgroo leaf+smile wordmark on transparent (706x340)",
    "bedford": "PASS — Bedford script + swoosh + 'Delikat essen', recoloured dark (501x184)",
    "costa": "PASS (small) — blue COSTA with shrimp-O on white brush (304x121)",
    "beyond-meat": "PASS — black BEYOND MEAT 2022 wordmark (SVG 1024x123)",
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
    "run": "2026-10-14T0404 Daten-Squad",
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
ev = f"{DATEN}/raw/logos_squad_2026-10-14T0404.json"
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
