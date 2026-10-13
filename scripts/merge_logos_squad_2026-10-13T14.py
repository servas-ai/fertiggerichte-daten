"""Daten-Squad 2026-10-13T14 logo merge: additive (new keys + fill file-less rows + producer-logo aliases).
Every new logo was visually checked via Read vision gate (correct brand, sharp, no placeholder, no product photo, usable on light bg)."""
import json, shutil, os, datetime, csv

G = "Vision gate 2026-10-13T14 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T14")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

# slug, name, brands, file, source, origin-note, hq
NEW = [
    ("delidip", "deli dip", ["Deli Dip", "deli dip", "DeliDip"], "delidip.png",
     "https://cdn.prod.website-files.com/67390534eec8342a659fdf85/6746d27b797228be2c2a4363_delidip-webclip.png",
     "offizielles Webclip/Logo delidip.com (Webflow CDN; deli gourmet GmbH, Nußdorferplatz 5/9, 1190 Wien – Impressum geprüft); Kreis-Badge freigestellt", True),
    ("ablinger", "Ablinger", ["Ablinger"], "ablinger.png",
     "https://www.ablinger.co.at/wp-content/uploads/2025/06/ABL_Logo.svg",
     "offizielles Logo ablinger.co.at (Franz Ablinger & Co Fleischhauereibetrieb GmbH, Oberndorf – Impressum geprüft); aus SVG-eingebettetem PNG übernommen", True),
    ("farniente", "Farniente", ["Farniente"], "farniente.png",
     "https://static.wixstatic.com/media/90a877_cde4c3f864a84b8499b47a47b73bce94~mv2.png",
     "offizielles Logo farniente.be (Farniente S.A., Seilles/Andenne, Belgien = Hersteller lt. Gurkerl); schwarzer BG freigestellt", True),
    ("biogourmet", "BioGourmet", ["BioGourmet", "Bio Gourmet"], "biogourmet.png",
     "https://bio-gourmet.com/wp-content/uploads/2018/01/bigo_logo_rgb-1.png",
     "offizielles Logo bio-gourmet.com (BioGourmet GmbH, Erdmannhausen – Impressum geprüft)", True),
    ("zum-dorfkrug", "Zum Dorfkrug", ["Zum Dorfkrug"], "zum-dorfkrug.svg",
     "https://www.zum-dorfkrug.de/assets/zum-dorfkrug-logo.svg",
     "offizielles Header-Logo zum-dorfkrug.de (Waldgrün #005e39 auf transparent – helles UI ok)", True),
]

# Producer/brand aliases onto EXISTING file-backed rows
ALIAS = {
    "blasko": ["Blasko", "BLASKO"],                      # file existed, brands=[] → products unmatched
    "hink": ["Hink"],                                    # products also use brand 'Hink' (Gurkerl) besides 'Hink Wien'
    "tress-brueder": ["Küchenbrüder", "Kuechenbrueder", "Küchenbrueder"],  # Küchenbrüder → TressBrüder relaunch (same TRESS Lebensmittel)
    "every-foods": ["Every"],                            # OFF brand 'Every' vs Every.
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
    "run": "2026-10-13T14 Daten-Squad (non-Eigenmarke brand + company logos)",
    "added": [{k: d[k]["note"], "source": d[k]["source"]} for k in added],
    "updated_fileless": [{k: d[k]["note"], "source": d[k]["source"]} for k in updated],
    "aliases_producer_fallback": aliased,
    "rejected": {
        "The Green Garden (onobox.at/images/logo.png)": "Asset is the 'Ono' Onobox mark (green circle), not The Green Garden restaurant brand — wrong brand, rejected",
        "Mama / Thai President Foods Commons SVG": "File:Thai President Foods Logo.svg is the parent-company green mark, not the red MAMA wordmark — not assigned as Mama brand logo",
        "Namdong (Unilever)": "still HTTP 403 Akamai on Unilever brand pages — not bypassed; Commons has no Namdong noodle logo",
        "Wiener Virtshaus / BS Gastro": "no own website (known); not retried aggressively",
        "Pasta Box / Elsässer / Holzbauer / Just Veg! / Sushitime / Gastrotech": "no clean official logo asset found this run (sites missing, ambiguous entity, or Eigenmarke)",
        "Whollees / Hildegard-Grünkraft / Dairy 4 Fun / La Crêpe de Brocéliande": "TLS hostname mismatch or handshake fail — not bypassed (policy)",
        "Galana / Beldessert": "emmidesserts.com brands page HTTP 406; no clean Commons asset",
        "Eigenmarken (Good Choice, Pappudia, Chef Select, SPAR enjoy, dmBio, Vemondo, Nature's Gold, PIZZ'AH, M/MPreis, Kania, MCENNEDY, Chef Menü, Deluxe, Rettenswert, TANN, …)": "skipped by policy",
        "Staudinger / Ager / Njami-Glatz / Rügenwalder Mühle": "known dead ends (white lettering / icon-font / favicon-only / windmill icon)",
        "delidip.svg cream (#f2e8dc) footer SVG": "cream on transparent invisible on light bg — used webclip circle badge instead",
    },
    "counts": {"added": len(added), "updated_fileless": len(updated), "aliased": len(aliased), "total_rows": len(d)},
    "generated": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
}
ev = f"{DATEN}/raw/logos_squad_2026-10-13T14.json"
os.makedirs(f"{DATEN}/raw", exist_ok=True)
json.dump(evidence, open(ev, "w"), ensure_ascii=False, indent=1)
os.makedirs("/workspace/fertig/analysis/logo_work_T14", exist_ok=True)
json.dump(evidence, open("/workspace/fertig/analysis/logo_work_T14/evidence.json", "w"), ensure_ascii=False, indent=1)
print("added", added); print("updated_fileless", updated); print("aliased", aliased); print("total", len(d))
