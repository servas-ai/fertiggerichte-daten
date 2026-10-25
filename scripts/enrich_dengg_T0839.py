"""Dengg Krapfen- und Knödelmanufaktur webshop (dengg.info; dengg krapfen & knödel manufaktur GmbH, Innsbrucker Straße 11,
6060 Hall in Tirol; FN 376199i LG Innsbruck per Impressum; UID ATU67085156 VIES valid 2026-10-25 same name/address; GLEIF no
LEI) — 26 frozen savoury Tyrolean ready meals (Knödel, Schlutzkrapfen, Kaskrapfen). Source: food-connectors `dengg`
(category pages + product JSON-LD + official Produktdatenblatt PDFs → nutrition per 100 g, piece weight, ingredients).
Photos vision-checked 26/26. Shipping: frozen dry-ice parcel AT 20,00 € (DE 33,00 €), Wednesdays only. No GTIN.
Usage: python3 scripts/enrich_dengg_T0839.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import dengg as M

CSV = "data/online_mealprep.csv"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        x = d["extra"]; n = d["nutrition_100g"] or {}; size = d["size_g"]
        flags = [f"Preis {x['price_basis']}"]
        if n:
            flags.append("Nährwerte je 100 g lt. offiziellem Produktdatenblatt (PDF)")
        else:
            flags.append("Produktdatenblatt-Link 404 → keine Nährwerte, nicht geschätzt")
        if d["source_url"].split("/")[-1].replace("-de.html", "") in M.PACK_G:
            flags.append("Packungsgewicht 400 g lt. Packshot-Etikett (Vision)")
        elif size:
            flags.append(f"Packungsgewicht = {x['pieces']} Stück × {x['unit_g']:g} g lt. Datenblatt")
        else:
            flags.append("Packungsgewicht nicht publiziert (gemischte Stückgewichte) → leer")
        flags.append("keine GTIN publiziert")
        prot = n.get("proteins"); kcal = n.get("energy_kcal")
        pp = round(prot * size / 100, 1) if prot is not None and size else ""
        kp = round(kcal * size / 100) if kcal is not None and size else ""
        rows.append({"name": d["name"], "brand": "Dengg", "store": M.STORE, "price_eur": d["price_eur"], "size_g": size or "",
             "price_per_kg": d["unit_price_eur"] or "", "url": d["source_url"], "image_url": d["image_url"] or "",
             "kcal_100": kcal if kcal is not None else "", "protein_100": prot if prot is not None else "",
             "fat_100": n.get("fat", ""), "satfat_100": n.get("saturated_fat", ""), "carbs_100": n.get("carbohydrates", ""),
             "sugar_100": n.get("sugars", ""), "fiber_100": "", "salt_100": n.get("salt", ""),
             "protein_pack": pp, "kcal_pack": kp,
             "eur_per_10g_protein": round(d["price_eur"] / (pp / 10), 2) if pp else "",
             "manufacturer": d["producer"], "producer_id": "dengg", "origin": "AT (Tirol, Hall in Tirol)",
             "bio": False, "veg": x["veg"], "prep": "tiefgekühlt – in Salzwasser kochen bzw. erwärmen", "category": "Online Meal-Prep",
             "price_source": f"dengg.info Produktseite {day} (Standardpackung, inkl. 10 % MwSt, zzgl. Versand); {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "dengg.info Produktdatenblatt PDF je 100 g" if n else "",
             "packaging": f"{x['pieces']} Stück" + (f" à {x['unit_g']:g} g" if x["unit_g"] else "") if x["pieces"] else "",
             "online": True, "available": x["in_stock"], "storage": "tiefgekühlt", "shelf_life": "", "shipping_eur": M.SHIPPING_AT,
             "nut_flag": "; ".join(flags), "ean": "", "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.dengg.info/unsere-produkte/{knoedel,schlutzkrapfen,krapfen,saisonale-produkte}.html + product pages + Produktdatenblatt PDFs (1 req/s)",
           "fetched": stamp, "robots": "robots.txt: Disallow /cgi-bin only",
           "operator": "dengg krapfen & knödel manufaktur GmbH", "fn": "FN 376199i (LG Innsbruck, per Impressum)",
           "impressum": {"https://www.dengg.info/impressum.html": "dengg krapfen & knödel manufaktur Gmbh, Innsbrucker Straße 11, 6060 Hall in Tirol; GF Heidi und Roland Dengg; FN 376199i LG Innsbruck; UID ATU67085156"},
           "vies": {"uid": "ATU67085156", "valid": True, "checked": "2026-10-25T08:47:12Z", "name": "dengg krapfen & knödel manufaktur GmbH", "address": "Innsbrucker Straße 11, AT-6060 Hall in Tirol"},
           "gleif": "legalName filter 'dengg' 4 hits (Dengg Patisserie GmbH, Estrich-Technik Dengg & Tasser, two persons) — none is this company → no LEI",
           "shipping": {"https://www.dengg.info/verpackung-und-versand.html": "Tiefkühlprodukte werden ausschließlich mittwochs versandt und donnerstags ausgeliefert ... Versand innerhalb Österreich: € 20,00 Versand nach Deutschland: € 33,00; Zahlung per Paypal"},
           "retail": "Einzelhandel page lists BILLA, SPAR Tirol, Hörtnagl among stockists",
           "price_caveat": "page shows 'EUR x inkl. 10% MwSt zzgl. Versandkosten' (used); some renders show net only (then ×1.10, flagged); schema.org offer price not used (net render shows net ×1.2)",
           "photo_vision_gate": "26/26 PASS (Dengg packshots match product names; Kasnocken 280 g, Knödel 400 g labels)",
           "excluded": ["sweet Krapfen (Apfel-Feige-Nuss, Marillen, Maroni, Mohn, Preiselbeer, Stanzer Zwetschken, Kirchtagskrapfen, Kiachl)",
                        "sweet Knödel (Wachauer Marillen, Stanzer Zwetschken)", "sides (Semmelknödel, Sauerkraut, Erdäpfelblattl, Erdäpfelpaunzen, Butterbrösel, Teigblattl pikant)"],
           "kept": kept}
    json.dump(out, open(f"raw/dengg_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "dengg"]
    ap = sorted(r["price_eur"] for r in rows); ep = sorted(r["eur_per_10g_protein"] for r in rows if r["eur_per_10g_protein"] != "")
    comp.append({c: "" for c in ccols} | {"slug": "dengg", "name": "Dengg Krapfen- und Knödelmanufaktur", "role": "producer+retailer",
        "legal_name": "dengg krapfen & knödel manufaktur GmbH", "fn": "FN 376199i", "register_id": "FN 376199i", "register_authority": "Firmenbuch",
        "legal_form_code": "GmbH", "country": "AT", "address": "Innsbrucker Straße 11, AT-6060 Hall in Tirol", "entity_status": "UID VIES gültig; kein LEI",
        "owners": "", "website": "https://www.dengg.info", "product_count": len(rows), "median_price_eur": ap[len(ap) // 2],
        "median_eur_per_10g_protein": ep[len(ep) // 2] if ep else "", "fetched_at": stamp,
        "brands": "Dengg", "chains": M.STORE + "|BILLA|SPAR Tirol|Hörtnagl", "uid": "ATU67085156", "uid_vies_name": "dengg krapfen & knödel manufaktur GmbH",
        "uid_vies_address": "Innsbrucker Straße 11, AT-6060 Hall in Tirol", "uid_checked_at": "2026-10-25T08:47Z",
        "imprint_url": "https://www.dengg.info/impressum.html", "register_court": "LG Innsbruck", "registry_status": "fn_from_impressum_uid_vies_valid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
