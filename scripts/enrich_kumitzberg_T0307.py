"""Kumitzberg webshop (kumitzberg.at; Großarler Genuss GmbH, Sonneggweg 1, 5611 Großarl, Pongau, Salzburg; FN 473130f
LG Salzburg; UID ATU72344714 VIES valid 2026-10-25 same name/address; managing directors Thomas Ammerer, Jürgen
Höllmüller; EU approval AT 50774 EU (data/establishments.csv); GLEIF legalName/fulltext/registeredAs → 0, no LEI)
→ rows 'Online: Kumitzberg' in data/online_mealprep.csv (idempotent replace) + evidence raw/kumitzberg_<stamp>.json
+ new company row 'kumitzberg' (Daten-Squad 2026-10-25T0307).
Source: food-connectors `kumitzberg` adapter (public Shopify products.json, one request, + one product page per meal;
robots 'Allow: /') → 5 chilled heat-up meals. Nutrition only as printed on the product page (Rehragout, Spareribs,
Schweinsbraten — the latter printed as 'ca. 290 kcal', flagged); Knödel without nutrition → empty, never estimated;
Spareribs sugar printed '< 0,5 g' → left empty. No GTIN. Photos vision-checked: Rehragout jar packshot PASS, Tiroler-/
Kaspressknödel product cut-outs PASS, Schweinsbraten → 2nd image (cut-out roast with slices) PASS; Spareribs: both shop
images are styled BBQ-glazed serving scenes (corn, sauce) that do not show the mildly seasoned vacuum product → no
image_url (FAIL, not a product photo). Shipping (policies/shipping-policy): DHL chilled Tue/Thu, AT 9,90 €, free from 95 €.
Usage: python3 scripts/enrich_kumitzberg_T0307.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import kumitzberg as K

CSV = "data/online_mealprep.csv"
VIES = {"uid": "ATU72344714", "valid": True, "name": "Großarler Genuss GmbH",
        "address": "Sonneggweg 1, AT-5611 Großarl", "checked": "2026-10-25T03:08:47.255Z"}
IMG = {"schweinebraten-fertig-gebraten": 1, "sous-vide-spareribs": None}
META = {  # handle → (prep, packaging, portions, veg)
    "rehragout-im-glas-380g": ("essfertig im Glas – nur erhitzen", "Glas 380 g", 1, False),
    "tirolerknodel": ("gebacken & servierfertig – im Backrohr 180 °C ca. 10 min aufbacken oder in der Pfanne anbraten", "3 Stück, Schutzatmosphäre, ca. 420 g", 1, False),
    "kaspressknoedel": ("gebacken & servierfertig – in der Pfanne erwärmen oder im Backrohr 180 °C 10–12 min aufbacken", "3 Stück, Schutzatmosphäre, ca. 450 g", 1, True),
    "schweinebraten-fertig-gebraten": ("fertig gebraten – kalt aufschneiden oder im Backrohr 150–160 °C 20–30 min mit Suppe/Bratensaft erwärmen", "1 kg Braten gekühlt", None, False),
    "sous-vide-spareribs": ("sous-vide vorgegart – nur kurz im Ofen/Grill/Pfanne fertiggaren bzw. bräunen", "vakuumverpackt, ca. 1,2 kg", None, False),
}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in K.Kumitzberg().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; h = x["handle"]; size = d["size_g"]; n = d["nutrition_100g"] or {}
        prep, pack, portions, veg = META[h]
        i = IMG.get(h, 0); img = x["images"][i] if i is not None and len(x["images"]) > i else ""
        flags = []
        flags.append("Nährwerte lt. Produktseite je 100 g" + (" (kcal als 'ca.' angegeben)" if x.get("nutrition_approx") else "") if n else "keine Nährwerte auf der Produktseite → nicht geschätzt")
        if h == "sous-vide-spareribs":
            flags.append("Zucker '< 0,5 g' → leer gelassen; Gewicht 'ca. 1,2 kg' lt. Titel; Shop-Bilder nur gestylte Serviervorschläge → kein Bild")
        flags.append("Zutaten lt. Produktseite (" + (x.get("ingredients") or "—") + "); keine GTIN")
        kcal, prot = n.get("kcal"), n.get("protein")
        rows.append({"name": d["name"], "brand": "Kumitzberg", "store": K.STORE, "price_eur": d["price_eur"], "size_g": int(size),
             "price_per_kg": d["unit_price_eur"], "url": d["source_url"], "image_url": img,
             "kcal_100": kcal, "protein_100": prot, "fat_100": n.get("fat"), "satfat_100": n.get("satfat"), "carbs_100": n.get("carbs"),
             "sugar_100": n.get("sugar"), "salt_100": n.get("salt"),
             "protein_pack": round(prot * size / 100, 1) if prot else None, "kcal_pack": round(kcal * size / 100) if kcal else None,
             "eur_per_10g_protein": round(d["price_eur"] / (prot * size / 100) * 10, 2) if prot else None,
             "manufacturer": K.PRODUCER, "producer_id": "kumitzberg", "origin": "AT", "bio": False, "veg": veg,
             "prep": prep, "category": "Online Meal-Prep",
             "price_source": f"kumitzberg.at Shopify products.json {day}, Preis je Packung inkl. USt; Versand DHL gekühlt AT 9,90 €, ab 95 € versandkostenfrei",
             "price_date": day, "nut_source": f"kumitzberg.at Produktseite {day}" if n else "", "packaging": pack, "online": True,
             "available": bool(x.get("available")), "storage": "gekühlt +2 bis +6 °C", "shelf_life": "", "shipping_eur": 9.9,
             "nut_flag": "; ".join(flags), "ean": None, "portions": portions})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != K.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": K.BASE + "/products.json?limit=250 + /products/<handle>", "fetched": stamp, "operator": K.PRODUCER, "vies": VIES,
           "gleif": "GLEIF legalName 'Großarler Genuss GmbH', fulltext 'Großarler', registeredAs 'FN 473130f' → 0 records (2026-10-25), no LEI",
           "impressum": K.BASE + "/policies/legal-notice (Großarler Genuss GmbH, Sonneggweg 1, 5611 Großarl; FN 473130f, LG Salzburg; ATU72344714; GF Thomas Ammerer, Jürgen Höllmüller; Unternehmensgegenstand Erzeugung und Onlinehandel mit Lebensmitteln)",
           "eu_approval": "AT 50774 EU (data/establishments.csv, Großarler Genuss GmbH, Sonneggweg 1, 5611 Großarl)",
           "robots": "User-agent * Allow: / (Shopify storefront); products.json once + 1 page per meal via polite helper",
           "shipping": K.SHIPPING_NOTE, "note": "shop page 'Versand' mentions 'Testbetrieb' next to the 2026 EU withdrawal button; products, prices and stock are live",
           "photo_vision_gate": "4/5 PASS (Rehragout jar packshot; Tiroler-/Kaspressknödel cut-outs; Schweinsbraten 2nd image cut-out) — Spareribs FAIL (styled BBQ serving scenes only) → no image",
           "excluded": ["Wild-Leberpasteten 100 g (Aufstrich, product_type Fertiggericht)", "Gebackene Leberknödel 3 Stk (Suppeneinlage)",
                        "Leberkäse/Käse-/Chili-Leberkäse 500 g (Wurstware)", "Selchschopf, Speck, Würste, Käse, Aufstriche, Gewürze, Genussbox"],
           "kept": kept}
    json.dump(out, open(f"raw/kumitzberg_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "kumitzberg"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "kumitzberg", "name": "Kumitzberg", "role": "producer",
        "legal_name": "Großarler Genuss GmbH", "fn": "FN 473130f", "register_id": "FN 473130f", "register_authority": "Firmenbuch",
        "register_court": "Landesgericht Salzburg", "legal_form_code": "GmbH", "country": "AT",
        "address": "Sonneggweg 1, AT-5611 Großarl", "entity_status": "UID aktiv (VIES valid); FN lt. Impressum; kein LEI",
        "owners": "GF Thomas Ammerer, Jürgen Höllmüller (lt. Impressum)", "website": K.BASE, "product_count": len(rows), "median_price_eur": prices[len(prices) // 2], "fetched_at": VIES["checked"],
        "brands": "Kumitzberg", "chains": K.STORE, "plants_count": 1, "uid": VIES["uid"], "uid_vies_name": VIES["name"],
        "uid_vies_address": VIES["address"], "uid_checked_at": VIES["checked"], "imprint_url": K.BASE + "/policies/legal-notice",
        "registry_status": "verified_vies_imprint"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    lp = "data/logos.csv"; lg = list(csv.DictReader(open(lp, encoding="utf-8"))); lcols = list(lg[0].keys())
    lg = [r for r in lg if r["slug"] != "kumitzberg"]
    lg.append({"slug": "kumitzberg", "name": "Kumitzberg", "category": "Markenhersteller", "file": "logos/kumitzberg.png",
        "source_url": "https://kumitzberg.at/cdn/shop/files/304703661_450783080403934_6356363052378405272_n_b2cdcd41-3a16-4c70-bc7d-20e653517b38.jpg (site header logo alt 'Kumitzberg.at', KB monogram + KUMITZBERG wordmark; robots allow; 400x400 → PNG; vision gate PASS; staged in fertiggerichte-daten scripts/logo_work_T0307 for the Orchestrator merge)",
        "brands": "Kumitzberg|Großarler Genuss|Online: Kumitzberg"})
    with open(lp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lg)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
