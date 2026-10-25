"""Purer Genuss (purer-genuss.at) — own webshop of the Burgenland brand 'Schüsseltrieb Manufaktur' (Wild im Glas: venison from
Burgenland hunting associations, processed by Fleischerei Hatwagner, cooked at Weinstube Szemes). Operator Szemes GmbH,
Hauptstraße 33, 7423 Pinkafeld, Bezirk Oberwart, Burgenland (FN 660812 h, LG Eisenstadt; UID ATU82450358 VIES valid
2026-10-25T07:12Z, same name/address; GLEIF 0 hits → no LEI; GF/Gesellschafter Philipp Szemes, Tina Posch per szemes.net Impressum)
→ rows 'Online: Purer Genuss (Schüsseltrieb)' in data/online_mealprep.csv (idempotent replace) + evidence
raw/purergenuss_<stamp>.json + company row 'szemes' (Daten-Squad 2026-10-25T0715).
Source: food-connectors `purergenuss` adapter (WooCommerce Store API, 1 request) → 7 ready meals of 20 products
(Wild Jus/Wildsugo = sauces and GINeins gin excluded).
No description, ingredients, nutrition, GTIN or net fill weight published → empty, never estimated (product pages show only the
WooCommerce shipping weight 'Gewicht 0,4 kg', not a declared fill quantity). Shipping fee not published (cart only) → empty;
pickup in Pinkafeld by phone per szemes.net. Press (meinbezirk 2020/2022): heat-preserved jars, chilled, up to ~9 months, no
preservatives → noted in nut_flag only. Photos: packshots HEAD 200 and vision-checked 7/7 PASS.
Usage: python3 scripts/enrich_purergenuss_T0715.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import purergenuss as M

CSV = "data/online_mealprep.csv"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        flags = ["keine Nährwerte/Zutaten/GTIN auf purer-genuss.at → nicht geschätzt",
                 "keine Füllmenge veröffentlicht (nur Versandgewicht 0,4 kg) → size_g leer",
                 "Wildfleisch aus burgenländischen Jagdgesellschaften, Verarbeitung Fleischerei Hatwagner, gekocht Weinstube Szemes (Presse meinbezirk)",
                 "Versandkosten nicht veröffentlicht; Abholung Pinkafeld nach tel. Vereinbarung"]
        rows.append({"name": d["name"], "brand": d["brand"], "store": M.STORE, "price_eur": d["price_eur"],
             "size_g": "", "price_per_kg": "", "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": "Schüsseltrieb Manufaktur (Szemes GmbH, 7423 Pinkafeld, Burgenland; mit Fleischerei Hatwagner, Oberpullendorf)",
             "producer_id": "szemes", "origin": "AT (Burgenland; Wild aus burgenländischen Jagdgesellschaften lt. Presse)",
             "bio": False, "veg": False, "prep": "im Glas – erwärmen", "category": "Online Meal-Prep",
             "price_source": f"purer-genuss.at WooCommerce Store API {day}, Preis/Glas inkl. MwSt. zzgl. Versand",
             "price_date": day, "nut_source": "", "packaging": "Glas", "online": True,
             "available": bool(d["extra"].get("in_stock")),
             "storage": "gekühlt (Glaskonserve, lt. Presse bis ca. 9 Monate haltbar)", "shelf_life": "",
             "shipping_eur": "", "nut_flag": "; ".join(flags), "ean": None, "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": M.BASE + "/wp-json/wc/store/v1/products?per_page=100 (WooCommerce Store API, 1 request)", "fetched": stamp,
           "robots": "allows shop/product pages and wp-json; disallows only wp-admin, WooCommerce upload/log folders, add-to-cart",
           "operator": "Szemes GmbH", "fn": "FN 660812 h", "court": "Landesgericht Eisenstadt",
           "impressum": {"purer-genuss.at": "Weinstube Familienbetrieb Szemes, Inhaber Philipp Szemes (no FN/UID printed)",
                         "szemes.net": "Szemes GmbH, Hauptstraße 33, 7423 Pinkafeld; FN 660812 h LG Eisenstadt; UID ATU82450358; GF + 50/50 Gesellschafter Philipp Szemes, Tina Posch; gasthaus@szemes.net, +43 3357 42305"},
           "vies": {"uid": "ATU82450358", "valid": True, "checked": "2026-10-25T07:12:30Z", "name": "Szemes GmbH",
                    "address": "Hauptstraße 33, AT-7423 Pinkafeld"},
           "gleif": "fulltext 'Szemes' / fuzzycompletions → 0 records → no LEI",
           "hatwagner": "hatwagner.at TLS connect error (not retried/bypassed) → FN/UID not collected",
           "shipping": M.SHIPPING_NOTE, "photo_vision_gate": "7/7 PASS (HEAD 200, jar packshots with matching label)",
           "excluded": ["sauces: Wild Jus (Saucenbasis, 5,99 €), Wildsugo (8,50 €)", "non-food: GINeins gin products"],
           "kept": kept}
    json.dump(out, open(f"raw/purergenuss_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "szemes"]
    ap = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "szemes", "name": "Schüsseltrieb Manufaktur / Weinstube Szemes (Purer Genuss)",
        "role": "producer", "legal_name": "Szemes GmbH", "fn": "FN 660812h",
        "register_id": "FN 660812 h", "register_authority": "Firmenbuch (Landesgericht Eisenstadt)", "legal_form_code": "GmbH",
        "country": "AT", "address": "Hauptstraße 33, AT-7423 Pinkafeld", "entity_status": "UID VIES gültig; kein LEI",
        "owners": "Philipp Szemes 50 %, Tina Posch 50 % (GF beide)", "website": M.BASE, "product_count": len(rows),
        "median_price_eur": ap[len(ap) // 2], "fetched_at": stamp, "brands": "Schüsseltrieb Manufaktur", "chains": M.STORE,
        "uid": "ATU82450358", "uid_vies_name": "Szemes GmbH", "uid_vies_address": "Hauptstraße 33, AT-7423 Pinkafeld",
        "uid_checked_at": "2026-10-25T07:12Z", "imprint_url": "https://www.szemes.net/index.php/kontakt/impressum", "register_court": "Landesgericht Eisenstadt",
        "registry_status": "fn_from_imprint_uid_vies_valid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
