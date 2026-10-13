"""Daten-Squad 2026-10-13T12:44 company/producer logo merge: additive new keys + fill file-less rows.
Every logo was visually checked via Read vision gate (correct company, sharp, no placeholder, no product photo, usable on light bg)
and the entity was cross-checked against the company's own site (imprint/legal name) or the dataset's website field."""
import json, shutil, os, datetime
W = "/workspace/fertig/analysis/logo_work_T13co"  # finals mirrored in scripts/logo_work_T13_companies; LOGOS_DIR = "/workspace/fertig/analysis/logos"; P = "/workspace/fertig/analysis/logos.json"
G = "Vision gate 2026-10-13T12:44 (Daten-Squad, Firmenlogos): visuell geprüft (korrekte Firma/Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
site = {o["slug"]: o for o in json.load(open(f"{W}/site.json"))}
cm = json.load(open(f"{W}/cm_meta.json"))
def s(slug, i): return site[slug]["cands"][i]["url"]
NEW = [  # slug, name, category, brands, source, origin note
 ("alimentastic", "Alimentastic", "Markenhersteller", [], s("alimentastic", 0), "offizielles og:image alimentastic.com (Alimentastic GmbH, 'House of Brands'; Feelfood-Vertrieb) – Firmenlogo, nicht Feelfood-Markenlogo"),
 ("bauck", "Bauck Mühle", "Bio", ["Bauck Mühle", "Bauck", "Bauckhof"], s("bauck", 2), "offizielles Logo bauck.de (Bauck GmbH, 'Bauck Mühle seit 1969')"),
 ("cecchin", "Cecchin", "Markenhersteller", ["Cecchin", "Fratelli Cecchin"], s("cecchin", 0), "offizielles og:image pastacecchin.it (Laboratorio Alimentare Cecchin Andrea e Carlo srl, Pastafresca)"),
 ("ehrenwort", "ehrenwort", "Bio", ["ehrenwort", "Ehrenwort"], s("ehrenwort", 1), "offizielles og:image ehrenwort.at (Ehrenwort GmbH, Bio-Gewürze; Website laut companies.csv)"),
 ("greisinger", "Greisinger", "Produzent/Werk", ["Greisinger"], s("greisinger", 0), "offizielles Header-Logo greisinger.com (Impressum: Greisinger GmbH – Fleisch-, Wurst- und Selchwaren)"),
 ("hamker", "Hamker", "Markenhersteller", [], s("hamker", 0), "offizielles Header-Logo hamker.de (Impressum: Hamker Vertriebsgesellschaft mbH) – Firmenlogo, nicht Marinus-Markenlogo"),
 ("heiderbeck", "Heiderbeck", "Markenhersteller", [], s("heiderbeck", 0), "offizielles Header-Logo heiderbeck.de (Impressum: Heiderbeck GmbH) – Firmenlogo, nicht Casa-di-Pietro-Markenlogo"),
 ("hiel", "Hiel", "Bio", ["Hiel"], s("hiel", 0), "offizielles og:image hiel.at (Hiel & Co GmbH / Peter Hiel, vegetarische Bio-Genussmanufaktur seit 1988)"),
 ("mochi", "Mochi", "Markenhersteller", ["Mochi"], s("mochi", 1), "offizielles Wortmarken-Logo mochi.at (Mochi Wien; Produkte 'Mochi Production GmbH, 1020 Wien' bei Gurkerl)"),
 ("rila", "Rila", "Markenhersteller", [], s("rila", 1), "offizielles Header-Logo rila.de (Impressum: RILA Feinkost-Importe GmbH & Co. KG) – Firmenlogo, nicht Jürgen-Langbein-Markenlogo"),
 ("tops-foods", "Tops Foods", "Markenhersteller", [], s("tops-foods", 5), "offizielles Site-Icon topsfoods.com (TOPS FOODS NV, Olen BE, VAT BE0451.053.4) – Firmenlogo, nicht Pure-Markenlogo"),
 ("rewe-group", "REWE Group", "Handelskette", [], cm["rewe-group"]["page"], f"Wikimedia Commons ({cm['rewe-group']['license']}) File:REWE GROUP Logo 10-2026–.svg – Konzernlogo für REWE International AG"),
 ("mars", "Mars", "Markenhersteller", [], cm["mars"]["page"], f"Wikimedia Commons ({cm['mars']['license']}) File:Mars Incorporated 2019 logo.svg – Konzernlogo für Mars Austria OG (nicht Ben's-Original-Markenlogo)"),
]
d = json.load(open(P)); added, filled = [], []
for slug, name, cat, brands, src, orig in NEW:
    fn = f"{slug}.png"; shutil.copy(f"{W}/final/{fn}", os.path.join(LOGOS_DIR, fn))
    e = dict(slug=slug, name=name, brands=brands, logo_category=cat, file="logos/" + fn, source=src, size="png", note=f"{G} · {orig}", hq=True)
    if slug in d:
        if d[slug].get("file"): print("skip file-backed", slug); continue
        e["brands"] = list(dict.fromkeys((d[slug].get("brands") or []) + brands)); filled.append(slug)
    else: added.append(slug)
    d[slug] = e
json.dump(d, open(P + ".tmp", "w"), ensure_ascii=False, indent=1); os.replace(P + ".tmp", P)
ev = {"run": "2026-10-13T12:44 Daten-Squad (Firmen-/Herstellerlogos)",
 "added": {k: d[k]["note"] for k in added}, "filled_fileless": {k: d[k]["note"] for k in filled},
 "app_companies_matcher": "scripts/app_companies.py: brand-alias fallback (company brand == any file-backed logo name/alias) + explicit REWE International→REWE Group, Mars Austria→Mars",
 "rejected": {
  "Rügenwalder Mühle": "ruegenwalder.de only exposes the windmill icon without wordmark (shape-only, same policy as Findus); no Commons hit",
  "Glatz GmbH (Njami)": "glatz.at shows only a red 'G' favicon; entity link to Njami unverified",
  "REWE International (rewe-group.at)": "page assets are BILLA/BIPA/PENNY/IKI chain logos + building photo, no REWE International logo → Commons REWE GROUP 10-2026 logo used",
  "Zum Dorfkrug": "zumdorfkrug.de is a domain-for-sale page (EliteDomains)",
  "Franuí": "franui.com SSL EOF", "Galana": "galana.be HTTP 406", "Whollees / Winkelbauer / BioGourmet": "TLS hostname mismatch (not bypassed)",
  "deli gourmet / Stangl / Ablinger / Ager": "guessed domains NXDOMAIN (no verified official site)",
  "Staudinger / Amlacher": "unrelated redirect / parking page (T12)",
 },
 "generated": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")}
json.dump(ev, open("/workspace/fertiggerichte-daten/raw/logos_companies_2026-10-13T13.json", "w"), ensure_ascii=False, indent=1)
print("added", added, "filled", filled, "total", len(d))
