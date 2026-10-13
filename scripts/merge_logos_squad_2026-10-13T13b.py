"""Daten-Squad 2026-10-13T13b logo merge: additive (new keys + fill file-less rows + producer-logo aliases).
Every new logo was visually checked via Read vision gate (correct brand, sharp, no placeholder, no product photo, usable on light bg)."""
import json, shutil, os, datetime

G = "Vision gate 2026-10-13T13b (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T13b")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
CMN = "https://commons.wikimedia.org/wiki/File:Logo_Conditorei_Coppenrath_%26_Wiese.png"

# slug, name, brands, file, source, origin-note, hq
NEW = [
    ("wagner", "Original Wagner", ["Wagner", "Original Wagner", "Nestlé Wagner"], "wagner.png",
     "https://www.original-wagner.de/",
     "offizielles Header-Logo original-wagner.de (Inline-SVG; Farben aus Site-CSS für hellen Header: --color--navy #004876, Peel/Swoosh; Original Wagner Pizza GmbH, Nonnweiler)", True),
    ("amlacher", "Amlacher Nudel", ["Amlacher", "Amlacher Nudeln", "Amlacher Nudel"], "amlacher.png",
     "https://amlachernudel.com/wp-content/uploads/amlacher-nudel-logo.jpg.jpeg",
     "offizielles Logo amlachernudel.com (Amlacher Nudel GmbH, Äußere Einöde); auf Wortmarke 'NUDELN Amlacher' zugeschnitten (Hausgrafik + Adresszeile entfernt), 480px-Quelle", False),
    ("ackerl", "Ackerl", ["Ackerl", "ACKERL"], "ackerl.png",
     "https://www.weinbergmaier.at/images/ackerl.png",
     "offizielles Markenlogo weinbergmaier.at (Weinbergmaier GmbH, Wolfern – Marke ACKERL, = Hersteller lt. Billa-Produktdaten)", True),
    ("stangl", "Stangl Nudeln", ["Stangl", "Stangl Nudeln", "Stangl Teigwaren"], "stangl.png",
     "https://stanglnudeln.at/cdn/shop/files/StanglnudelnLogo.png?v=1692648650",
     "offizielles Header-Logo stanglnudeln.at (Stangl Teigwaren GmbH, Lebring = Hersteller lt. Billa); 212px", False),
    ("frank-juice", "frank.", ["Frank Soup", "frank", "frank juice"], "frank.png",
     "https://thefrankjuice.com/cdn/shop/files/frank_logo_schwarz_-_frankjuice_png.png?v=1668438293",
     "offizielles Logo thefrankjuice.com (frank. – Säfte & 'frank soups' im Glas)", True),
    ("volante", "Volante PIZZZA! per casa", ["Volante PIZZZA per casa", "Volante", "Pizzza Volante"], "volante.png",
     "https://static.wixstatic.com/media/406b0d_a7d548fa932046d88068a72fd344612a~mv2.png",
     "offizielles Logo 'Volante PIZZZA! per casa' pizzza-volante.com (Bake-at-home-Linie, Wien)", True),
    ("coppenrath-wiese", "Coppenrath & Wiese", ["Coppenrath & Wiese", "Conditorei Coppenrath & Wiese", "Coppenrath und Wiese"], "coppenrath-wiese.png",
     CMN, "Wikimedia Commons (CC BY 4.0) File:Logo Conditorei Coppenrath & Wiese.png", True),
    ("gaon", "GAON", ["GAON - Koreanisches Restaurant", "GAON", "Gaon"], "gaon.png",
     "https://www.gaon-vienna.com/xstorage/1/_cache/20240423/GAON_Logo_black_281_1_5159b4ae78ffa4424552b77e0a315a5e.svg",
     "offizielles Logo gaon-vienna.com (GAON Koreanisches Restaurant, Apollogasse 20, 1070 Wien = Kontakt auf Gurkerl-Produktseiten)", True),
    ("freda", "Freda", ["Freda", "FREDA"], "freda.png",
     "https://www.eatfreda.com/",
     "offizielles Header-Logo eatfreda.com (Inline-SVG, currentColor = Site-Textfarbe rgb(199,17,17); siu foods GmbH, Passau = Hersteller lt. Billa)", True),
    ("blue-elephant", "Blue Elephant", ["Blue Elephant"], "blue-elephant.png",
     "https://blueelephant.com/wp-content/uploads/2024/12/BE-logo-beaten-gold-1.webp",
     "offizielles Logo blueelephant.com ('beaten gold'-Variante; Gold auf hellem BG lesbar, mittlerer Kontrast); 339px", False),
    ("wojnars", "Wojnar's", ["Wojnar's", "Wojnar", "WOJNAR'S"], "wojnars.png",
     "https://www.wojnar.at/wp-content/uploads/2023/11/Logowojnarclaim-rgb.png",
     "offizielles Logo wojnar.at (WOJNAR'S Wiener Leckerbissen)", True),
    ("dovgan", "Dovgan", ["DOVGAN", "Dovgan"], "dovgan.png",
     "https://www.dovgan.de/assets/templates/redesign18/images/logo.png",
     "offizielles Header-Logo dovgan.de (Dovgan GmbH, Hamburg); 215px", False),
    ("kozy-shack", "Kozy Shack", ["Kozyshack", "Kozy Shack"], "kozy-shack.png",
     "https://www.kozyshack.com/getmedia/6ffb8a26-e94a-4681-8059-b9d3a9226acb/top-logo.webp?ext=.webp",
     "offizielles Header-Logo kozyshack.com; 230px", False),
    ("della-mamma", "Della Mamma", ["Della Mamma", "DELLA MAMMA"], "della-mamma.png",
     "https://www.della-mamma.de/cdn/shop/files/DOL_DM_Logo_schwarz_1200x1200.png?v=1756479227",
     "offizielles Logo della-mamma.de (Retail-Marke der Dolce GmbH, Neu-Ulm; Impressum geprüft)", True),
    ("oekoland", "Ökoland", ["Ökoland", "Oekoland"], "oekoland.png",
     "https://oekoland.de/wp-content/uploads/2023/08/oekoland-logo-1000x819-1.png",
     "offizielles Logo oekoland.de (Ökoland GmbH Nord)", True),
    ("suedtiroler-kochwerk", "Südtiroler Kochwerk", ["Südtiroler Kochwerk", "Kochwerk"], "suedtiroler-kochwerk.png",
     "https://www.pursuedtirol.com/media/image/f4/b3/b3/Logo_S%C3%BCdtiroler_Kochwerk.png",
     "Markenlogo von der Herstellerseite 'WP Fine Food / Südtiroler Kochwerk' im Shop pursuedtirol.com (Pur Südtirol); keine eigene Marken-Website auffindbar – Händler-gehostet, daher hq=false", False),
    ("rians", "Rians", ["Rians", "Rians Crémerie"], "rians.png",
     "https://cremerie.rians.com/app/themes/rians/library/images/logo-rians.svg",
     "offizielles Header-Logo cremerie.rians.com (Rians Crémerie, Groupe Triballat)", True),
    ("oyakata", "Oyakata", ["Oyakata", "OYAKATA"], "oyakata.png",
     "https://oyakata.be/wp-content/themes/oyakata/assets/img/logo-round.svg",
     "offizielles Header-Logo oyakata.be (Ajinomoto); weiße Wortmarke auf schwarzer Header-Fläche als Badge zugeschnitten", True),
    ("basenbox", "Basenbox", ["Basenbox", "BASENBOX"], "basenbox.png",
     "https://www.basenbox.life/",
     "offizielles Header-Logo basenbox.life (Inline-SVG mit Originalfarben)", True),
    ("john-west", "John West", ["John West"], "john-west.png",
     "https://www.john-west.co.uk/wp-content/uploads/2024/11/logo_320x230_1_transparent.png",
     "offizielles Logo john-west.co.uk; 320px", False),
]

# Producer-logo fallback aliases onto EXISTING file-backed rows (brand has no own clean logo; producer verified via product producer field / imprint)
ALIAS = {
    "alimentastic": ["feelfood", "Feelfood", "Feel Food"],      # Feelfood vertrieben von Alimentastic (T13 company evidence)
    "tops-foods": ["Pure", "PURE"],                            # Billa 'PURE' Fertiggerichte: Hersteller Tops Foods NV
    "heiderbeck": ["Casa di Pietro"],                          # producer: Heiderbeck, Olching
    "hamker": ["Marinus"],                                     # producer: Hamker Vertriebsgesellschaft mbH, Dissen
    "rila": ["Jürgen Langbein"],                               # producer: 'Rila. Die Genussentdecker.'
    "greisinger": ["Original Greisinger"],                     # Greisinger Hausmarke
    "andros": ["Gourmand&Vegetal"],                            # product 'Andros Vegan Milchreis', producer Andros Deutschland GmbH
}

d = json.load(open(P))
added, updated, aliased = [], [], []
for slug, name, brands, fn, src, orig, hq in NEW:
    sp = os.path.join(FINAL, fn); assert os.path.exists(sp), sp
    entry = dict(slug=slug, name=name, brands=brands, logo_category="Markenhersteller", file="logos/" + fn,
                 source=src, size="png", note=f"{G} · {orig}", hq=hq)
    if slug in d:
        old = d[slug]
        if old.get("file") and os.path.exists("/workspace/fertig/analysis/" + old["file"]):
            print("skip existing file-backed", slug); continue
        entry["brands"] = list(dict.fromkeys((old.get("brands") or []) + brands))
        shutil.copy(sp, os.path.join(LOGOS_DIR, fn)); d[slug] = entry; updated.append(slug)
    else:
        assert not os.path.exists(os.path.join(LOGOS_DIR, fn)), "file name collision " + fn
        shutil.copy(sp, os.path.join(LOGOS_DIR, fn)); d[slug] = entry; added.append(slug)

for k, al in ALIAS.items():
    v = d[k]
    assert v.get("file") and os.path.exists("/workspace/fertig/analysis/" + v["file"]), k
    b = v.get("brands") or []
    new = [a for a in al if a not in b]
    if new:
        v["brands"] = b + new; aliased.append((k, new))

tmp = P + ".tmp"; json.dump(d, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, P)

evidence = {
    "run": "2026-10-13T13b Daten-Squad (non-Eigenmarke brand logos)",
    "added": [{k: d[k]["note"], "source": d[k]["source"]} for k in added],
    "updated_fileless": [{k: d[k]["note"], "source": d[k]["source"]} for k in updated],
    "aliases_producer_fallback": aliased,
    "rejected": {
        "Namdong (Unilever)": "unilever.co.uk/.nl/.de/.at brand pages HTTP 403 (Akamai) – not bypassed; Commons has no Namdong noodle logo (only Incheon Namdong-gu)",
        "La Fermière": "official SVG logo-la-fermiere.svg uses predominantly #fff fills → invisible on light bg (re-checked, same as T11/T12)",
        "innocent": "innocentdrinks.at logo asset is cream (#fffbe8-ish) on transparent → invisible on light bg",
        "Staudinger (holzofenspezialitaeten.at)": "staudinger_logo.png 238px with white 'HOLZOFEN SPEZIALITÄTEN' lettering (invisible on light bg); banner-only crop cuts the arc; og:image is a product photo",
        "Ager (ager.cc)": "logo rendered via icon font (agericons), no image asset; favicon only",
        "Marie Morin": "marie-morin.fr legal notice forbids reproduction of logos without written authorization → respected",
        "Oyakata logo-mobile.png": "white-on-transparent (invisible); used header badge crop instead",
        "Elsässer": "generic brand label; Gurkerl copy points to Traiteur Kirn / importer Lamercantile – entity ambiguous, no logo assigned",
        "Atelier Délices": "Belgian dessert brand only distributed by Heiderbeck (distributor ≠ producer) → no alias; no official brand site found",
        "Wiener Virtshaus": "no own website (wienervirtshaus.at DNS fail); shop.brok.at HTTP 429 – not retried aggressively",
        "Pasta Box": "no producer/brand site identifiable (Gurkerl 'Lokale Erzeuger' without producer)",
        "Miil": "Rohlik/Gurkerl Eigenmarke → skipped by policy",
        "Rettenswert": "HOFER Eigenmarke → skipped by policy",
        "TANN": "SPAR-Fleischwerk Eigenmarke → skipped by policy",
        "Deli Dip / Franuí / Ablinger / Rians.com / mariemorin.fr / freda-pizza.de / siu-foods.de / wpfinefood.com": "guessed domains NXDOMAIN/SSL fail (franui.com SSL EOF as in T13co)",
        "Njami (Glatz)": "glatz.at/njami 404; Glatz only red 'G' favicon (T13co)",
        "Eigenmarken (Good Choice, Pappudia, Chef Select, SPAR enjoy, dmBio, Vemondo, Nature's Gold, PIZZ'AH, M/MPreis, Kania, MCENNEDY, Chef Menü, GOOD, Milsani, Crane …)": "skipped by policy (Aldi CDN 403, no clean assets)",
    },
    "counts": {"added": len(added), "updated_fileless": len(updated), "aliased": len(aliased), "total_rows": len(d)},
    "generated": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
}
ev = "/workspace/fertiggerichte-daten/raw/logos_squad_2026-10-13T13b.json"
json.dump(evidence, open(ev, "w"), ensure_ascii=False, indent=1)
json.dump(evidence, open("/workspace/fertig/analysis/logo_work_T13b/evidence.json", "w"), ensure_ascii=False, indent=1)
print("added", added); print("updated_fileless", updated); print("aliased", aliased); print("total", len(d))
