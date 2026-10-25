"""Moakt.at (online shop of the regional MoaktLaden, Florianigasse 5, 8160 Weiz, Steiermark; operator Verein 'Weiz is(s)t
regional – Verein zur Steigerung der regionalen Lebensmittelversorgung und -qualität im Genussraum Weiz', ZVR 1009369655,
UID ATU80009358 VIES valid 2026-10-25 (VIES address Kleeweg 1, 8160 Weiz; Impressum Vereinssitz Hauptplatz 7); association → no
LEI) → rows 'Online: Moakt.at (Weiz)' in data/online_mealprep.csv (idempotent replace) + evidence raw/moakt_<stamp>.json
+ company rows 'moakt' and 'feiertag' (Daten-Squad 2026-10-25T0633).
Source: food-connectors `moakt` adapter (vendor grids + product pages, 1 req/s) → 15 regional ready meals from 5 producers.
No nutrition and no GTIN published → empty, never estimated. Size only where published (Feiertag 400 g, Gemisch 430 ml,
Wildragout 400 ml); Robert kocht and Biohof Hirschbauer publish no weight → empty.
Photos: primary product photos vision-checked 13/13 PASS; Hirschbauer Zwiebel-/Beuschelsuppe have no own photo → empty.
Delivery: click & collect Weiz or Friday home delivery Raum Weiz only, 7 €, free from 70 €.
Usage: python3 scripts/enrich_moakt_T0633.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import moakt as M

CSV = "data/online_mealprep.csv"
VEG = ("berglinsen", "champignon", "kuerbissuppe", "spinat-teigtaschen", "vegetarisches-chili")
PREP = {"robert-kocht": ("vorgekocht, schockgefrostet – erwärmen (Teigtaschen: 4 min in Salzwasser ziehen lassen)", "tiefgekühlt"),
        "qualitaetsfleischerei-feiertag": ("essfertig im Glas – erwärmen", ""),
        "gemisch": ("im Glas – erwärmen", ""), "hirsch-und-mehr": ("im Glas – erwärmen", ""),
        "biohof-hirschbauer": ("eingekocht im Glas, servierfertig – erwärmen", "")}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        x = d["extra"]; v = x["vendor"]; prep, storage = PREP[v]
        flags = ["keine Nährwerte im Shop → nicht geschätzt",
                 f"Zutaten lt. Produktseite: {x.get('ingredients') or 'nicht veröffentlicht'}; keine GTIN",
                 ("Füllmenge " + x["size_label"]) if x.get("size_label") else "keine Füllmenge veröffentlicht → leer, nicht geschätzt"]
        if not d["image_url"]:
            flags.append("kein eigenes Produktfoto im Shop")
        rows.append({"name": d["name"], "brand": d["brand"], "store": M.STORE, "price_eur": d["price_eur"],
             "size_g": int(d["size_g"]) if d["size_g"] else "", "price_per_kg": d["unit_price_eur"] or "",
             "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": d["producer"], "producer_id": {"qualitaetsfleischerei-feiertag": "feiertag"}.get(v, v),
             "origin": "AT", "bio": v == "biohof-hirschbauer", "veg": any(k in d["source_id"] for k in VEG),
             "prep": prep, "category": "Online Meal-Prep",
             "price_source": f"moakt.at Produktseite {day}, Preis inkl. USt (schema.org itemprop=price)",
             "price_date": day, "nut_source": "", "packaging": "Glas" if v != "robert-kocht" else "",
             "online": True, "available": True, "storage": storage, "shelf_life": "", "shipping_eur": 7.0,
             "nut_flag": "; ".join(flags), "ean": None, "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": M.BASE + " (GrandNode vendor pages + product pages, 1 req/s)", "fetched": stamp,
           "operator": "Weiz is(s)t regional – Verein zur Steigerung der regionalen Lebensmittelversorgung und -qualität im Genussraum Weiz",
           "zvr": "1009369655", "vies": {"uid": "ATU80009358", "valid": True, "checked": "2026-10-25T06:37Z",
                                          "name": "Weiz is(s)t regional - Verein zur Steigerung der regionalen Lebensmittelversorgung und -qualität im Genussraum Weiz",
                                          "address": "Kleeweg 1, AT-8160 Weiz"},
           "gleif": "association; fulltext 'Feiertag Weiz' and 'Qualitätsfleischerei Feiertag' → 0 records → no LEI",
           "feiertag_impressum": "https://www.derfeiertag.at/impressum → HTTP 403 (not bypassed) → FN/UID not taken",
           "shipping": M.SHIPPING_NOTE, "photo_vision_gate": "13/13 PASS (2 items without own photo)",
           "excluded": ["sides: Spätzle, Rotkraut, Schupfnudeln, Topfenknödel, Semmelknödel, Süßkartoffel Gnocchi, Kürbisgemüse, Kaspressknödel",
                        "sauces/fonds: Rinder-Gulaschsaft, Rinder-Sugo, Rinder-Kraftsuppe, Wels-Sugo, Sauce Bolognese, Gemüsesugo, Sugo Bolognese mit Wild",
                        "non-meals: sausages, fats, spreads, bread, salads, gift boxes, raw fish/meat"],
           "kept": kept}
    json.dump(out, open(f"raw/moakt_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] not in ("moakt", "feiertag")]
    fr = [r for r in rows if r["producer_id"] == "feiertag"]; fp = sorted(r["price_eur"] for r in fr)
    ap = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "moakt", "name": "Moakt.at / MoaktLaden Weiz", "role": "retailer",
        "legal_name": "Weiz is(s)t regional – Verein zur Steigerung der regionalen Lebensmittelversorgung und -qualität im Genussraum Weiz",
        "register_id": "ZVR 1009369655", "register_authority": "Zentrales Vereinsregister", "legal_form_code": "Verein", "country": "AT",
        "address": "Hauptplatz 7, AT-8160 Weiz (Vereinssitz); MoaktLaden Florianigasse 5, 8160 Weiz", "entity_status": "UID VIES valid 2026-10-25; Verein → kein LEI",
        "website": M.BASE, "product_count": len(rows), "median_price_eur": ap[len(ap) // 2], "fetched_at": stamp,
        "brands": "Robert kocht; mein Glas (Feiertag); Gemisch; Hirsch und mehr...; Biohof Hirschbauer", "chains": M.STORE,
        "uid": "ATU80009358", "uid_vies_name": out["vies"]["name"], "uid_vies_address": out["vies"]["address"], "uid_checked_at": "2026-10-25",
        "registry_status": "vies_valid"})
    comp.append({c: "" for c in ccols} | {"slug": "feiertag", "name": "Qualitätsfleischerei Feiertag", "role": "producer",
        "legal_name": "Qualitätsfleischerei Feiertag GmbH", "legal_form_code": "GmbH", "country": "AT",
        "address": "Marburger Straße 45, AT-8160 Weiz", "entity_status": "EU-Zulassung AT 62671 (establishments.csv); Impressum derfeiertag.at HTTP 403 → FN/UID nicht erhoben; GLEIF 0 → kein LEI",
        "website": "https://www.derfeiertag.at", "product_count": len(fr), "median_price_eur": fp[len(fp) // 2] if fp else "",
        "fetched_at": stamp, "brands": "mein Glas", "chains": M.STORE, "plants_count": 1, "registry_status": "imprint_blocked"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
