"""Daten-Squad 2026-10-13T12 logo merge: additive (new keys + fill file-less rows + safe aliases).
Every new logo was visually checked via Read vision gate (correct brand, sharp, no placeholder, no product photo, usable on light bg)."""
import json, shutil, os, datetime

G = "Vision gate 2026-10-13T12 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(__file__), "logo_work_T12_final")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
CM = json.load(open("/workspace/fertig/analysis/logo_work_T12/cm_meta.json"))

def cm(k):
    m = CM[k]
    return m["page"], f"Wikimedia Commons ({m['license']})"

# slug, name, category, brands, file, source, origin-note
NEW = [
    ("youcook", "YOUCOOK", "Markenhersteller",
     ["Youcook", "YOUCOOK", "YouCook"], "youcook.png",
     "https://www.youcook-food.com/wp-content/uploads/2025/11/YOUCOOK_Logo-quer-freigestellt-1.png",
     "offizielles Header-Logo youcook-food.com (YOUCOOK GmbH, Köln; schwarzer BG entfernt)"),
    ("andros", "Andros", "Markenhersteller",
     ["Andros"], "andros.png",
     "https://www.andros.fr/wp-content/uploads/2023/04/Andros-new-logo.svg",
     "offizielles Logo andros.fr (Andros Austria GmbH Produkte)"),
    ("deflorian", "deFLORiAN", "Markenhersteller",
     ["Deflorian", "deFLORiAN", "Deflorian S.r.l."], "deflorian.png",
     "https://deflorian.tirol/cdn/shop/files/deFlorian_logo.svg?height=35&v=1776863303",
     "offizielles Header-Logo deflorian.tirol (Deflorian Tiefkühlspezialitäten, Gnadenwald; NICHT deflorian.it Interior)"),
    ("aia", "AIA", "Markenhersteller",
     ["AIA"], "aia.png",
     "https://backoffice.aiafood.com/uploads/logo_aia_7afa0707fc.svg",
     "offizielles Logo aiafood.com (AIA Agricola Italiana Alimentare S.p.A.; Veronesi)"),
    ("indomie", "Indomie", "Markenhersteller",
     ["Indomie"], "indomie.png", *cm("indomie") + ("Wikimedia Commons Indomie Logo.png",)[:1]),
    ("arla", "Arla", "Markenhersteller",
     ["Arla"], "arla.png",
     "https://www.arlafoods.de/UI/img/arla-logo.a7388293.svg",
     "offizielles Header-Logo arlafoods.de"),
    ("thiriet", "Maison Thiriet", "Markenhersteller",
     ["Thiriet", "Maison Thiriet"], "thiriet.png",
     "https://static.thiriet.com/source/common_public/theme/theme_front_1/image/header/logo-maison-thiriet.svg",
     "offizielles Header-Logo thiriet.com"),
    ("hammermuehle", "Hammermühle", "Markenhersteller",
     ["Hammermühle", "Hammermuehle"], "hammermuehle.png",
     "https://www.hammermuehle-shop.de/media/54/03/d3/1739868317/Hammermuehle-Logo_(11).svg?ts=1739868318",
     "offizielles Logo hammermuehle-shop.de (Hammermühle GmbH, glutenfrei seit 1967)"),
    ("landtmanns", "Landtmann's Original", "Markenhersteller",
     ["Landtmann's", "Landtmanns", "Landtmann's Original"], "landtmanns.png",
     "https://landtmanns-original.at/cdn/shop/files/LMO_LOGO_RGB_23_63b5bf60-94f7-499a-8528-a685280fd3b5.png?v=1695284467",
     "offizielles Logo landtmanns-original.at (Landtmann's Feine Patisserie)"),
    ("ashoka", "Ashoka", "Markenhersteller",
     ["Ashoka"], "ashoka.png",
     "https://ashokafoods.com/cdn/shop/files/Layer_1.png?v=1783063203",
     "offizielles Logo ashokafoods.com (ADF Foods)"),
    ("strauss", "Strauss", "Markenhersteller",
     ["Strauss"], "strauss.png",
     "https://www.straussjosef.it/themes/custom/whtheme/logo2025.svg",
     "offizielles Logo straussjosef.it (Strauss Josef GmbH, Südtirol Knödel)"),
    ("danke-bauer", "Danke Bauer", "Markenhersteller",
     ["Danke Bauer"], "danke-bauer.png",
     "https://dankebauer.com/wp-content/themes/danke-bauer/assets/danke-bauer-logo-v6-perf.svg",
     "offizielles Logo dankebauer.com (Kärntner Spezialitäten)"),
    ("shanshi", "Shan'shi", "Markenhersteller",
     ["Shan'shi", "Shan shi", "Shanshi"], "shanshi.png",
     "https://shan-shi.com/wp-content/uploads/2020/11/ShanShi-Logo.jpg",
     "offizielles Logo shan-shi.com"),
    ("riso-gallo", "Riso Gallo", "Markenhersteller",
     ["Riso Gallo"], "riso-gallo.png",
     "https://www.risogallo.it/cdn/shop/files/riso_gallo_logo_it.webp?v=1780040526",
     "offizielles Logo risogallo.it (Riso Gallo S.p.A.)"),
    ("esterhazy", "Esterhazy", "Markenhersteller",
     ["Esterhazy"], "esterhazy.png",
     "https://esterhazy.at/assets/img/logo/ezy-logo-x1.png",
     "offizielles Wortmarke esterhazy.at (Esterhazy Wild-Gerichte bei Gurkerl)"),
    ("galbani", "Galbani", "Markenhersteller",
     ["Galbani"], "galbani.png", *cm("galbani") + ("Wikimedia Commons LogoGalbani-06122021.png",)[:1]),
]

# Fix indomie/galbani tuples - cm returns (page, license_note); we need source=page, orig=license
# Rebuild those two cleanly:
NEW = [x for x in NEW if x[0] not in ("indomie", "galbani")]
NEW += [
    ("indomie", "Indomie", "Markenhersteller", ["Indomie"], "indomie.png",
     CM["indomie"]["page"], f"Wikimedia Commons ({CM['indomie']['license']}) File:Indomie Logo.png"),
    ("galbani", "Galbani", "Markenhersteller", ["Galbani"], "galbani.png",
     CM["galbani"]["page"], f"Wikimedia Commons ({CM['galbani']['license']}) File:LogoGalbani-06122021.png"),
]

# Safe aliases only to EXISTING file-backed rows
ALIAS = {
    "iglo": ["Iglo", "IGLO"],  # case variants (already covered via lower(), keep explicit)
}

d = json.load(open(P))
added, updated, aliased = [], [], []

for slug, name, cat, brands, fn, src, orig in NEW:
    src_path = os.path.join(FINAL, fn)
    assert os.path.exists(src_path), src_path
    shutil.copy(src_path, os.path.join(LOGOS_DIR, fn))
    entry = dict(
        slug=slug, name=name, brands=brands, logo_category=cat,
        file="logos/" + fn, source=src, size="png",
        note=f"{G} · {orig}", hq=True,
    )
    if slug in d:
        old = d[slug]
        # fill file-less or overwrite only if previously no file
        if not old.get("file"):
            # merge brands
            b = list(dict.fromkeys((old.get("brands") or []) + brands))
            entry["brands"] = b
            d[slug] = entry
            updated.append(slug)
        else:
            print("skip existing file-backed", slug)
            continue
    else:
        d[slug] = entry
        added.append(slug)

for k, al in ALIAS.items():
    v = d[k]
    assert v.get("file") and os.path.exists("/workspace/fertig/analysis/" + v["file"]), k
    b = v.get("brands") or []
    new = [a for a in al if a not in b]
    if new:
        v["brands"] = b + new
        aliased.append((k, new))

tmp = P + ".tmp"
json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1)
os.replace(tmp, P)

evidence = {
    "run": "2026-10-13T12 Daten-Squad",
    "added": [{k: d[k]["note"]} for k in added],
    "updated_fileless": [{k: d[k]["note"]} for k in updated],
    "aliases": aliased,
    "rejected": {
        "Good Choice / Aldi CDN": "Aldi CDN 403; hofer.at only yields Aldi chain logos, not Good Choice wordmark; Commons empty",
        "Pappudia": "Rohlik/Gurkerl Eigenmarke; gurkerl.at only exposes Gurkerl logo; no Commons / no dedicated brand page logo",
        "dmBio": "dm.at/dm.de brand pages only yield dm chain favicons; no dmBio wordmark asset; Commons empty",
        "Chef Select / Vemondo / Chef Menü": "Lidl Eigenmarken; no freigestelltes Logo; Commons only product photos",
        "SPAR enjoy": "file-less row notes white-on-transparent only; spar.at 403 on brand page; not aliased to SPAR (distinct sub-brand)",
        "GAON / The Green Garden / Mochi": "official domains NXDOMAIN / SSL fail / robots disallow; The Green Garden ≠ Asia Green Garden",
        "La Fermière": "official SVG is predominantly white fills → invisible on light bg (same as T11 reject)",
        "Feelfood": "feelfood.shop asset is abstract brush mark without wordmark; broken alpha",
        "Della Mamma / Casa di Pietro": "heiderbeck.com only exposes Heiderbeck producer logo, not brand wordmark",
        "Deflorian.it": "wrong entity (interior design); food brand is deflorian.tirol (accepted)",
        "AIA Commons / aia.it": "wrong entities (referees association / Associazione Italiana Allevatori); food logo from aiafood.com accepted",
        "Amlacher": "amlacher.com is aftermarket parking page",
        "Staudinger": "staudinger.at redirects to unrelated stoellnberger.com",
        "Findus": "findus.com redirects to Birds Eye UK; no clean Commons logo",
        "Milsani": "aldi-sued.de only yields Aldi logos",
        "Strauss Eis / Hammermühle wrong domains": "NXDOMAIN; resolved via straussjosef.it / hammermuehle-shop.de",
        "alias to file-less rows (Good Choice, Chef Menü, Nature's Gold, etc.)": "no logo file → no alias (T11 policy)",
    },
    "checked_unresolved": [
        "Good Choice", "Pappudia", "dmBio", "Chef Select", "SPAR enjoy", "GAON - Koreanisches Restaurant",
        "The Green Garden", "Vemondo", "Chef Menü", "Amlacher", "Mochi", "M / MPreis Eigenmarke",
        "Cecchin", "Stangl", "Ackerl", "Wiener Virtshaus", "Volante PIZZZA per casa", "Frank Soup",
        "feelfood", "Kania", "Pure", "Greisinger", "Rettenswert", "Pasta Box", "Casa di Pietro",
        "Elsässer", "La Fermiere", "Atelier Délices", "Della Mamma", "Rians", "Milsani", "Deli Dip",
        "Njami", "PIZZ'AH", "Leibspeis'", "MCENNEDY", "Marinus", "TANN", "Haas", "Go", "Ager", "Asia",
    ],
    "counts": {"added": len(added), "updated_fileless": len(updated), "aliased": len(aliased), "total_rows": len(d)},
    "generated": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
}
ev_path = "/workspace/fertiggerichte-daten/raw/logos_squad_2026-10-13T12.json"
json.dump(evidence, open(ev_path, "w"), ensure_ascii=False, indent=1)
# also copy evidence into work dir
json.dump(evidence, open("/workspace/fertig/analysis/logo_work_T12/evidence.json", "w"), ensure_ascii=False, indent=1)
print("added", added)
print("updated_fileless", updated)
print("aliased", aliased)
print("total", len(d))
print("evidence", ev_path)
