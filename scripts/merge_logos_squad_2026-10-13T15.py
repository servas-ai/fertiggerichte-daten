"""Daten-Squad 2026-10-13T15 logo merge: additive (new keys + fill file-less rows + producer-logo aliases).
Every new logo was visually checked via Read vision gate (correct brand, sharp, no placeholder, no product photo, usable on light bg)."""
import json, shutil, os, datetime, csv

G = "Vision gate 2026-10-13T15 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T15")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

# slug, name, brands, file, source, origin-note, hq
NEW = [
    ("podravka", "Podravka", ["Podravka", "PODRAVKA"], "podravka.svg",
     "https://commons.wikimedia.org/wiki/File:Podravka_logo_2024.svg",
     "Wikimedia Commons File:Podravka logo 2024.svg (Public domain; Podravka d.d., Koprivnica – Hersteller lt. Brand-Tree)", True),
    ("heura", "Heura", ["Heura", "HEURA", "Heura Foods", "Foods for Tomorrow"], "heura.png",
     "https://commons.wikimedia.org/wiki/File:Logo_Heura_by_Foods_for_Tomorrow.png",
     "Wikimedia Commons File:Logo Heura by Foods for Tomorrow.png (Public domain); weißer BG freigestellt (Schwarz auf transparent)", True),
    ("nordsee", "Nordsee", ["Nordsee", "NORDSEE"], "nordsee.svg",
     "https://commons.wikimedia.org/wiki/File:Nordsee_Logo_2024.svg",
     "Wikimedia Commons File:Nordsee Logo 2024.svg (Public domain); LEH-Lizenzmarke von HOMANN Feinkost (Produzent lt. BILLA)", True),
    ("mama", "Mama", ["Mama", "MAMA"], "mama.png",
     "https://www.mama.co.th/en/images/logo-mama.png",
     "offizielles rotes MAMA-Wortmarken-Logo von mama.co.th (Thai President Foods PCL; robots.txt erlaubt /en/images); transparentes PNG 270×97 – NICHT das TF-Konzernlogo", True),
    ("maza", "Maza", ["Maza", "MAZA", "Maza Mediterranean Delicacies"], "maza.svg",
     "https://maza.at/wp-content/uploads/2024/07/logo.svg",
     "offizielles Logo maza.at (Maza Mediterranean Delicacies, Sluispolderweg 46, Zaandam NL – Kontakt/Impressum geprüft); petrol auf weißem Badge", True),
    ("englert", "Englert", ["Englert", "Feinkost Englert", "Englert Feinkost"], "englert.png",
     "https://feinkost-englert.de/_astro/responsive-logo-header.DtxL4qem_Z2mh27R.png",
     "offizielles Header-Logo feinkost-englert.de (Englert Feinkostspezialitäten GmbH & Co. KG, Lohr a. Main – Impressum geprüft); einfarbig weiß im Original → Füllfarbe auf #1f1f1f umgefärbt (Form unverändert) für helles UI", True),
]

# Brand aliases onto EXISTING file-backed rows (evidence in evidence['alias_reasons'])
ALIAS = {
    "omis-schmankerl": ["Omis"],         # OFF 9010437050456 'Gulasch vom Almo Rind': REWE-AT GS1-Präfix 9010437 + Omis-Schmankerl-Linie (BILLA Rindsgulasch)
    "danone": ["Danny"],                 # OFF 9035000007293 'Danone Dany Sahne Schoko' – Tippfehler-Marke, Produzent Danone
    "spar": ["Spar Linguine"],           # OFF 9100000987408 – SPAR-AT Eigenmarken-GS1-Präfix 9100000, Marke 'Spar'
}
REJECTED = {
    "Yopokki / Young Poong (ypfoods.co.kr, yopokki-us.com)": "ypfoods.co.kr: Box-Verbindung Timeout (40 s), WebFetch liefert nur Text ohne Bild-URLs; yopokki-us.com: TLS handshake failure (Box) bzw. HTTP 500 (WebFetch) – nicht umgangen; Commons ohne Yopokki-Logo",
    "Windisch (windisch-wurst.at)": "Website hat kein Bild-Logo (Text/Webfont); einziges Asset android-icon-192 = nur 'W'-Monogramm → reines Icon, abgelehnt",
    "innocent (innocentdrinks.de)": "einziges statisches Asset innocent_logo_RGB_cloud_solo.png = nur Engel-Icon in Creme (#fffbe9) – auf hellem UI unsichtbar, keine Wortmarke; Commons ohne innocent-Logo",
    "Findus": "en.wikipedia File:Findus logo.svg ist lokal 'Fair use' (nicht Commons); findus.it nur favicon.svg (Birds Eye) – abgelehnt",
    "Feinkost Leitinger (Marke 'Feinkost')": "feinkost-leitinger.at (Wix) nur weiße Logo-PNGs; zudem ist Markenstring 'Feinkost' generisch → kein sicherer Alias",
    "Thai Delight (NR Instant Produce)": "nrinstant.com zeigt Thai Delight nur als Produkt-Cover-Foto, kein Marken-Logo-Asset",
    "La Cocina de Lola": "lacocinadelola.com = Madrider Catering-'Quinta Gama'; Zuordnung zum Gazpacho (Importeur Antonio Viani) nicht verifiziert",
    "Mama / Thai President Foods TF-Logo": "weiterhin nicht verwendet; stattdessen echte rote MAMA-Wortmarke von mama.co.th übernommen",
    "Namdong / The Green Garden / Wiener Virtshaus / Pasta Box / Elsässer / Holzbauer / Just Veg! / IDS (La Crêpe TLS) / Harvest (Whollees TLS) / Galana (406)": "bekannte Sackgassen aus T13b/T14 – nicht erneut forciert",
    "Eigenmarken (Good Choice, Pappudia, dmBio, Chef Select, SPAR enjoy, Chef Menü, Vemondo, M, GOOD, Kania, Nature's Gold, PIZZ'AH, Leibspeis', MCENNEDY, Asia, Go, TANN, FK, Wild, GOLDEN, Pik., Le Gourmet, Lorado, El Tequito, Ocean Sea, Taste Of Asia, Penny Ready, Diamond, SELECT&GO, …)": "per Policy übersprungen",
}

d = json.load(open(P))
added, updated, aliased = [], [], []
for slug, name, brands, fn, src, orig, hq in NEW:
    sp = os.path.join(FINAL, fn); assert os.path.exists(sp), sp
    entry = dict(slug=slug, name=name, brands=brands, logo_category="Markenhersteller", file="logos/" + fn,
                 source=src, size=fn.rsplit(".", 1)[-1], note=f"{G} · {orig}", hq=hq)
    if slug in d:
        old = d[slug]
        if old.get("file") and os.path.exists("/workspace/fertig/analysis/" + old["file"]):
            print("skip existing file-backed", slug); continue
        entry["brands"] = list(dict.fromkeys((old.get("brands") or []) + brands))
        shutil.copy(sp, os.path.join(LOGOS_DIR, fn)); d[slug] = entry; updated.append(slug)
    else:
        dest = os.path.join(LOGOS_DIR, fn)
        assert not os.path.exists(dest), "file name collision " + fn
        shutil.copy(sp, dest); d[slug] = entry; added.append(slug)

for k, al in ALIAS.items():
    v = d[k]
    assert v.get("file") and os.path.exists("/workspace/fertig/analysis/" + v["file"]), k
    b = v.get("brands") or []
    new = [a for a in al if a not in b]
    if new:
        v["brands"] = b + new; aliased.append((k, new))

# Also fill file-less kuechenbrueder / every rows by pointing brands already covered via alias
# (coverage matches brands on file-backed rows — aliases above suffice)

tmp = P + ".tmp"; json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, P)

# Sync data/logos.csv + logos.json (list form) without touching product tables
logos_rows = [{"slug": k, "name": v.get("name"), "category": v.get("logo_category"), "file": v.get("file"),
               "source_url": v.get("source"), "brands": v.get("brands")} for k, v in d.items()]
json.dump(logos_rows, open(f"{DATEN}/data/logos.json", "w"), ensure_ascii=False, indent=1)
with open(f"{DATEN}/data/logos.csv", "w", newline="") as fh:
    fields = ["slug", "name", "category", "file", "source_url", "brands"]
    w = csv.DictWriter(fh, fields); w.writeheader()
    for r in logos_rows:
        w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})

evidence = {
    "run": "2026-10-13T15 Daten-Squad (non-Eigenmarke brand logos)",
    "added": [{k: d[k]["note"], "source": d[k]["source"]} for k in added],
    "updated_fileless": [{k: d[k]["note"], "source": d[k]["source"]} for k in updated],
    "aliases_producer_fallback": aliased,
    "rejected": REJECTED,
    "alias_reasons": {
        "Omis→omis-schmankerl": "OFF 9010437050456 (Gulasch vom Almo Rind): GS1-Präfix 9010437 = REWE International (BILLA/PENNY/Clever) und Omis Schmankerl ist die BILLA-Fertiggerichtlinie inkl. Rindsgulasch",
        "Danny→danone": "OFF 9035000007293 heißt 'Danone Dany Sahne Schoko' – Marke falsch geschrieben (Dany), Hersteller Danone; Produzenten-Logo-Fallback",
        "Spar Linguine→spar": "OFF 9100000987408: GS1-Präfix 9100000 = SPAR Österreich Eigenmarke; Markenstring enthält 'Spar'",
    },
    "counts": {"added": len(added), "updated_fileless": len(updated), "aliased": len(aliased), "total_rows": len(d)},
    "generated": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
}
ev = f"{DATEN}/raw/logos_squad_2026-10-13T15.json"
os.makedirs(f"{DATEN}/raw", exist_ok=True)
json.dump(evidence, open(ev, "w"), ensure_ascii=False, indent=1)
os.makedirs("/workspace/fertig/analysis/logo_work_T15", exist_ok=True)
json.dump(evidence, open("/workspace/fertig/analysis/logo_work_T15/evidence.json", "w"), ensure_ascii=False, indent=1)
print("added", added); print("updated_fileless", updated); print("aliased", aliased); print("total", len(d))
