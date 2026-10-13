"""Daten-Squad 2026-10-13T2340 logo merge: next Eigenmarke/brand gaps via official packshot crops.
Vision gate: each crop inspected via Read (correct brand wordmark, legible, not a product photo /
generic icon). Sources: packshots already in the dataset (SPAR CDN / dm-static / Gurkerl CDN / OFF).
No Aldi CDN Brandpage-Logo re-probe (known 403). No login/cookies/JS-bypass."""
import json, shutil, os, datetime, csv, hashlib

G = "Vision gate 2026-10-13T2340 (Daten-Squad): visuell geprüft (korrekte Marke, scharf, kein Platzhalter/Produktfoto, auf hellem Hintergrund nutzbar)"
FINAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_work_T2340")
LOGOS_DIR = "/workspace/fertig/analysis/logos"
P = "/workspace/fertig/analysis/logos.json"
DATEN = "/workspace/fertiggerichte-daten"

# slug, name, brands, file, source, origin-note, hq, category
NEW = [
    ("vemondo", "Vemondo", ["Vemondo", "Vemondo, Grønvang Food ApS, Lidl"], "vemondo.png",
     "OFF packshot GTIN 4056489848752 front_de.11 (Vemondo veganer Salat nach Art eines Budapester Salates) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Lidl-Eigenmarke VEMONDO (weißes Wordmark mit Blatt-V auf hellgrünem Blatt); 3000x4000 OFF-Foto; Commons kein Treffer", True, "Eigenmarke"),
    ("nature-s-gold", "Nature's Gold", ["Nature's Gold", "NATURE'S GOLD"], "natures-gold.png",
     "OFF packshot GTIN 4099200105291 front_de.25 (Nature's Gold Pfannengemüse Feinschmecker Art) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Hofer-Eigenmarke NATURE'S GOLD (weiße Handschrift auf Kreidetafel-Badge); Aldi-CDN Brandpage-Logo bewusst nicht geprobt (T09 403)", True, "Eigenmarke"),
    ("yum-yum", "Yum Yum", ["Yum Yum", "YumYum"], "yum-yum.png",
     "MPreis Cloudinary packshot (res.cloudinary.com/dit8huoga, Yum Yum Instantnudeln Huhn, GTIN 8852018101024) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Wan Thai Foods Marke YumYum® (grün/gelbes Wordmark auf gelbem Pack-Header)", True, "Markenhersteller"),
    ("kania", "Kania", ["Kania", "Kania (Lidl)"], "kania.png",
     "OFF packshot GTIN 4335619175334 front_en.3 (Kania India Style Yellow Curry) — Ausschnitt Markenlogo",
     "Packshot-Ausschnitt Lidl-Eigenmarke Kania (weißes Script-Wordmark mit Smile-Bogen auf rotem Tab); Quelle 1275x1698, Crop auf 300px hochskaliert, lesbar", True, "Eigenmarke"),
    ("m-mpreis", "M (MPreis Eigenmarke)", ["M (MPreis Eigenmarke)", "M"], "m-mpreis.png",
     "MPreis Cloudinary packshot (res.cloudinary.com/dit8huoga, M Cevapcici mit Letscho und Reis) — Ausschnitt Eigenmarken-Siegel",
     "Packshot-Ausschnitt MPreis-Eigenmarke M (weißes M im roten Quadrat, wie auf der Verpackung); eigener Eintrag statt Alias auf mpreis.svg, weil der Pack-Aufdruck das Eigenmarken-Siegel ist", True, "Eigenmarke"),
    ("leitgebs", "Leitgeb's Nudelspezialitäten", ["Leitgeb's Nudelspezialitäten", "Leitgeb´s", "Leitgeb's"], "leitgebs.png",
     "Gurkerl CDN packshot Leitgeb´s Vegetarischer Nudelteller (cdn.gurkerl.at …/40027-1741767351370.jpg, GTIN 9120071330248) — Ausschnitt Etikett-Sticker",
     "Packshot-Ausschnitt gelber Leitgeb's-Sticker (Handgemachte Nudeln + Nudel-Maskottchen + Script-Wordmark); Quelle nur 637px, Crop hochskaliert, Wordmark lesbar; Leitgeb-Website nicht geprobt in diesem Lauf", True, "Markenhersteller"),
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
        shutil.copy(sp, os.path.join(LOGOS_DIR, fn)); d[slug] = entry; updated.append(slug)
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
import collections
bc = collections.Counter()
with open(f"{DATEN}/data/products.csv") as fh:
    for row in csv.DictReader(fh):
        bc[(row.get("brand") or "").strip()] += 1
impact = {}
for slug in added + updated:
    brands = d[slug]["brands"]
    impact[slug] = sum(bc.get(b, 0) for b in brands)

evidence = {
    "run": "2026-10-13T2340 Daten-Squad",
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
        "The Green Garden (6 products)": "Gurkerl images are plated-meal photos (Gurkerl own-label collab) with no packaging logo; no packshot available — still open",
        "Vemondo Smoothie Bowl / Geschnetzeltes OFF fronts": "logo absent or 300px only — used 3000x4000 Budapester front instead",
        "Wikimedia Commons (Vemondo/Nature's Gold/Kania/Yum Yum/Leitgeb's)": "not used — pack crops from dataset packshots",
    },
    "counts": {
        "added": len(added), "updated_fileless": len(updated),
        "total_rows": len(d),
        "with_file": sum(1 for v in d.values() if (v.get("file") or "").strip()),
        "products_impacted_total": sum(impact.values()),
    },
    "sha256": sha,
}
ev = f"{DATEN}/raw/logos_squad_2026-10-13T2340.json"
os.makedirs(f"{DATEN}/raw", exist_ok=True)
json.dump(evidence, open(ev, "w"), ensure_ascii=False, indent=1)
print("added", added)
print("updated_fileless", updated)
print("impact", impact)
print("total", len(d), "with_file", evidence["counts"]["with_file"])
for slug in added + updated:
    assert os.path.exists(os.path.join(LOGOS_DIR, d[slug]["file"].split("/",1)[1]))
    assert d[slug]["file"]
print("ok")
