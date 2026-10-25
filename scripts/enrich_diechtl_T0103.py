"""Fleischerei Diechtl webshop (diechtl-shop.at; Fleischerei Diechtl Erich Ernst e.U., Inh. Erich Ernst Diechtl,
Hauptstraße 31, 8983 Bad Mitterndorf, Steiermark; FN 338325m LG Leoben; UID ATU41616104 VIES valid 2026-10-25
'Diechtl Erich jun', Bad Mitterndorf 31; GLEIF fulltext 'Diechtl' → 0 records, no LEI)
→ rows 'Online: Fleischerei Diechtl' in data/online_mealprep.csv (idempotent replace) + evidence raw/diechtl_<stamp>.json
+ new company row 'diechtl' (Daten-Squad 2026-10-25T0103).
Source: food-connectors `diechtl` adapter (public Shopware 6 HTML, robots allow except '/*?'; category 'feinkost-im-glas'
ItemList JSON-LD + product-page Product JSON-LD at 1 req/s) → 1 jar meal (Rindsgulasch im Glas 390 g 8,99 €).
Excluded: Gulaschsaft, Bolognese (sauces), Rinderbrühe (clear broth / cooking base); the 9 /detail/ pages are raw-meat
Raclette/Fondue/Bratwurst/Bratl boxes, not ready meals. No nutrition and no GTIN on page or label → empty, never
estimated. Ingredients/allergens transcribed from the label on the shop's own packshot (evidence crops in
scripts/logo_work_T0103). Photo: vision gate 1/1 PASS (single jar 'DIECHTL Rindergulasch im GLAS').
Shipping: Kühlpaket within Austria, 1–3 working days, 6,90 € below 70 €, free from 70 €."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import diechtl as D

CSV = "data/online_mealprep.csv"
VIES = {"uid": "ATU41616104", "valid": True, "name": "Diechtl Erich jun", "address": "Bad Mitterndorf 31, AT-8983 Bad Mitterndorf",
        "checked": "2026-10-25T00:07:21.646Z"}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in D.Diechtl().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]
        r = {"name": d["name"], "brand": "Fleischerei Diechtl", "store": D.STORE, "price_eur": d["price_eur"], "size_g": int(size),
             "price_per_kg": round(d["price_eur"] / size * 1000, 2), "url": d["source_url"], "image_url": d["image_url"],
             "manufacturer": D.PRODUCER, "producer_id": "diechtl", "origin": "AT", "bio": False, "veg": False,
             "prep": "Im Topf bei mittlerer Hitze unter Rühren erwärmen oder im offenen Glas in der Mikrowelle", "category": "Online Meal-Prep",
             "price_source": f"diechtl-shop.at Produktseite {day} (schema.org JSON-LD), Preis pro Glas {int(size)} g inkl. MwSt.; Kühlpaket innerhalb Österreichs, 6,90 € unter 70 €, ab 70 € versandkostenfrei",
             "price_date": day, "nut_source": "", "packaging": f"Glas {int(size)} g", "online": True,
             "available": x.get("availability") == "InStock", "storage": x.get("label_storage") or x.get("storage") or "",
             "shelf_life": x.get("shelf_life") or "", "shipping_eur": D.SHIPPING_EUR,
             "nut_flag": ("keine Nährwerte auf Produktseite oder Etikett → nicht geschätzt; Zutaten/Allergene vom Etikett auf dem Shop-Foto "
                          "transkribiert (" + (x.get("ingredients") or "—") + "); keine GTIN"),
             "ean": None, "portions": 1}
        rows.append(r)
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != D.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": D.CATEGORY + " + product pages", "fetched": stamp, "operator": D.PRODUCER, "vies": VIES,
           "gleif": "GLEIF fulltext 'Diechtl' → 0 records (2026-10-25), no LEI",
           "impressum": D.BASE + "/Impressum/ (Fleischerei Diechtl Erich Ernst e.U., Inh. Erich Ernst Diechtl, Hauptstraße 31, A-8983 Bad Mitterndorf; FN 338325m; LG Leoben; UID ATU41616104; Aufsicht BH Liezen; WKÖ Lebensmittelgewerbe)",
           "robots": "User-agent * Allow / ; Disallow /*? /account/ /checkout/ /widgets/ ; only query-free pages and /media/*?ts= images fetched",
           "shipping": D.SHIPPING_NOTE, "photo_vision_gate": "1/1 PASS (single jar packshot, label 'DIECHTL Rindergulasch im GLAS'; label shows an older price 7,99 €, live price 8,99 €)",
           "label_transcription": "ingredients/allergens/storage read from the label on the shop packshot 5awdk5t8.png (crop scripts/logo_work_T0103/diechtl_rindsgulasch_etikett.jpg)",
           "excluded": ["Gulaschsaft im Glas 390 g 4,50 € (Sauce)", "Bolognese im Glas 390 g 7,99 € (Sauce)",
                        "Rinderbrühe im Glas 390 g 4,49 € (klare Brühe/Kochbasis)",
                        "9 /detail/ variant pages: Raclette/Fondue/Bratwurst/Bratl-Box (rohes Fleisch, kein Fertiggericht)"],
           "kept": kept}
    json.dump(out, open(f"raw/diechtl_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "diechtl"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "diechtl", "name": "Fleischerei Diechtl", "role": "producer",
        "legal_name": "Fleischerei Diechtl Erich Ernst e.U.", "fn": "FN 338325m", "register_id": "FN 338325m", "register_authority": "Firmenbuch",
        "legal_form_code": "e.U.", "country": "AT", "address": "Hauptstraße 31, AT-8983 Bad Mitterndorf",
        "entity_status": "UID aktiv (VIES valid); kein LEI", "owners": "Erich Ernst Diechtl (Inhaber lt. Impressum)",
        "website": D.BASE, "product_count": len(rows), "median_price_eur": prices[len(prices) // 2], "fetched_at": VIES["checked"],
        "brands": "Fleischerei Diechtl|Diechtl", "chains": D.STORE, "uid": VIES["uid"], "uid_vies_name": VIES["name"],
        "uid_vies_address": VIES["address"], "uid_checked_at": VIES["checked"], "imprint_url": D.BASE + "/Impressum/",
        "register_court": "Landesgericht Leoben", "registry_status": "verified_vies_imprint"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
