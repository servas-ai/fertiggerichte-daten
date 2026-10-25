"""Bullinarium online shop (bullinarium.com) — 'Fix & Fertig' ready meals of Hallers Bull Beef® (Haller Kreislaufwirtschaft,
Markt Allhau, Bezirk Oberwart, Burgenland). Operator per shop AGB: Haller GmbH, Gemeindestraße 30, 7411 Markt Allhau
(FN 492415s, Landesgericht Eisenstadt; UID ATU73356147 VIES valid 2026-10-25T07:41:51Z with same name/address;
GLEIF fulltext/legalName/registeredAs → no LEI). Corrects the earlier hub note that Bullinarium had no shop
(bullinarium.at is the old TYPO3 site; the shop lives at bullinarium.com/de/online-shop/).
→ rows 'Online: Bullinarium (Hallers Bull Beef)' in data/online_mealprep.csv (idempotent replace) + evidence
raw/bullinarium_<stamp>.json + company row 'haller' (Daten-Squad 2026-10-25T0739).
Source: food-connectors `bullinarium` adapter (Fix & Fertig category page + product-page schema.org JSON-LD, 1 s apart)
→ 4 ready meals of 9 category items (Sugo, BBQ Sauce, Chili Mayo, Essence = sauces/condiments, Fix & Fertig Duo = bundle of
the two jars → excluded). No nutrition and no GTIN published → empty, never estimated. Chili size is a volume (0,35 l)
→ size_g 350 with 'Füllmenge 0,35 l' flag (same convention as other ml jars). Photos vision-checked 4/4 PASS.
Usage: python3 scripts/enrich_bullinarium_T0739.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import bullinarium as M

CSV = "data/online_mealprep.csv"
PREP = {"33020": ("essfertig im Schraubglas – nur erwärmen", "Glas 350 g"),
        "33071": ("essfertig im Glas – nur erwärmen", "Glas 0,35 l"),
        "33031": ("im Ganzen langsam geschmort – im Beutel erwärmen, dann ca. 40 min bei 165 °C im Rohr fertigstellen", "Vakuumbeutel 2,8 kg"),
        "33012": ("über Stunden niedrig gegart – im Rohr fertigstellen", "Packung (Box) 1,2 kg")}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        x = d["extra"]; prep, pack = PREP.get(str(d["source_id"]), ("erwärmen", ""))
        flags = ["keine Nährwerte und keine GTIN auf bullinarium.com → nicht geschätzt",
                 f"Zutaten lt. Produktseite: {x['ingredients']}" if x.get("ingredients") else "Zutaten nicht veröffentlicht",
                 f"Art.Nr. {x.get('sku')}"]
        if x.get("size_label", "").endswith(" l"):
            flags.append(f"Füllmenge {x['size_label']} (Volumen, als g übernommen)")
        if x.get("persons"):
            flags.append(f"ausreichend für {x['persons']} Personen lt. Produktseite")
        if x.get("on_request"):
            flags.append("derzeit ausverkauft – 'auf Anfrage lieferbar'")
        rows.append({"name": d["name"], "brand": d["brand"], "store": M.STORE, "price_eur": d["price_eur"],
             "size_g": d["size_g"] or "", "price_per_kg": d["unit_price_eur"] or "", "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": "Bullinarium-Küche – Haller GmbH, Gemeindestraße 30, 7411 Markt Allhau, Burgenland (FN 492415s, UID ATU73356147)",
             "producer_id": "haller", "origin": "AT (Burgenland; Hallers Bull Beef aus eigener Kreislauflandwirtschaft Markt Allhau)",
             "bio": False, "veg": False, "prep": prep, "category": "Online Meal-Prep",
             "price_source": f"bullinarium.com Produktseite (schema.org Offer) {day}, inkl. 10 % USt.; {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "", "packaging": pack, "online": True,
             "available": bool(x.get("in_stock")), "storage": "gekühlt 2–4 °C (Kühlkettenversand)", "shelf_life": "",
             "shipping_eur": M.SHIPPING_EUR, "nut_flag": "; ".join(flags), "ean": None, "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": M.CATEGORY_URL + " + product pages (schema.org Product JSON-LD), 1 s apart", "fetched": stamp,
           "robots": "disallows only /typo3*/, /t3lib/, /tslib/, /typo3conf/, /fileadmin/template/, /de/online-shop/kassa/, /de/online-shop/order-handling/",
           "operator": "Haller GmbH", "fn": "FN 492415s", "court": "Landesgericht Eisenstadt",
           "impressum": {"https://www.bullinarium.com/service/impressum/": "Bullinarium / Hallers Bull Beef, Markt Allhau (no FN/UID printed)",
                         "https://www.bullinarium.com/shopnavigation/agbs/": "Haller GmbH, Gemeindestraße 30, 7411 Markt Allhau; FN 492415s LG Eisenstadt; UID ATU73356147; tel. +43 3356 22212"},
           "vies": {"uid": "ATU73356147", "valid": True, "checked": "2026-10-25T07:41:51Z", "name": "Haller GmbH",
                    "address": "Gemeindestraße 30, AT-7411 Markt Allhau"},
           "gleif": "fulltext 'Haller GmbH Markt Allhau' 0 hits; legalName 'Haller GmbH' AT → only unrelated Haller companies; registeredAs 492415s 0 → no LEI",
           "shipping": M.SHIPPING_NOTE, "photo_vision_gate": "4/4 PASS (Gulasch + Chili box packshots, braised Wade, glazed BBQ ribs)",
           "excluded": ["bundle: Fix & Fertig Duo vom Bull Beef 21,11 € (Gulasch + Chili jars)", "sauces/condiments: Bull Beef Sugo 350g, BBQ Sauce 350ml, Chili Mayo 250ml, Bull Beef Essence",
                        "outside Fix & Fertig: raw cuts, burger patties, Bullinger sausages, pastrami, boxes, gin, vouchers"],
           "correction": "COVERAGE T-note claimed 'bullinarium.at TYPO3 without shop' — the shop is live at bullinarium.com/de/online-shop/",
           "kept": kept}
    json.dump(out, open(f"raw/bullinarium_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "haller"]
    ap = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "haller", "name": "Hallers Bull Beef / Bullinarium",
        "role": "producer", "legal_name": "Haller GmbH", "fn": "FN 492415s",
        "register_id": "FN 492415s", "register_authority": "Firmenbuch (Landesgericht Eisenstadt)", "legal_form_code": "GmbH",
        "country": "AT", "address": "Gemeindestraße 30, AT-7411 Markt Allhau", "entity_status": "UID VIES gültig; kein LEI",
        "website": "https://www.bullinarium.com", "product_count": len(rows),
        "median_price_eur": ap[len(ap) // 2], "fetched_at": stamp, "brands": "Hallers Bull Beef|Bullinarium", "chains": M.STORE,
        "uid": "ATU73356147", "uid_vies_name": "Haller GmbH", "uid_vies_address": "Gemeindestraße 30, AT-7411 Markt Allhau",
        "uid_checked_at": "2026-10-25T07:41Z", "imprint_url": "https://www.bullinarium.com/shopnavigation/agbs/", "register_court": "Landesgericht Eisenstadt",
        "registry_status": "fn_from_agb_uid_vies_valid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
