"""Flotte Lotte webshop (flottelottezwettl.at; Flotte Lotte GmbH, Pater Werner Deibl Strasse 5, 3910 Zwettl NÖ; FN 550284 t
LG Krems an der Donau per Impressum; UID ATU76539079 VIES valid 2026-10-25; GLN 9110029937544; GLEIF no LEI) — 15 vegan,
gluten- and lactose-free jar ready meals (8 Eintöpfe 380 g, 7 Suppen 380 ml) made from rescued surplus vegetables.
Source: food-connectors `flottelotte` (JTL-Shop category + product pages → price, Inhalt, Nährwerte per 100 g, Zutaten).
Photos vision-checked 13/13 (2 shop placeholders → empty). Shipping: chilled express AT 9,90 € (<75 €), 7,90 € (75–99,99 €),
free from 100 €. No GTIN on the shop.
Usage: python3 scripts/enrich_flottelotte_T0911.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import flottelotte as M

CSV = "data/online_mealprep.csv"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        x = d["extra"]; n = d["nutrition_100g"] or {}; size = d["size_g"]
        flags = [f"Preis {x['price_basis']}", "Nährwerte je 100 g lt. Produktseite"]
        if x["size_unit"] == "ml":
            flags.append("Inhalt 380 ml (Suppe) – ml als g übernommen")
        if n.get("kcal") is not None and all(n.get(k) is not None for k in ("fat", "carbs", "protein")):
            at = 9 * n["fat"] + 4 * n["carbs"] + 4 * n["protein"]
            if abs(at - n["kcal"]) > max(8, 0.25 * n["kcal"]):
                flags.append(f"Atwater ohne Ballaststoffe {at:.0f} kcal vs. deklariert {n['kcal']:g} kcal")
        if n.get("protein") == 0:
            flags.append("Eiweiß 0,0 g wie publiziert")
        if not d["image_url"]:
            flags.append("Shop zeigt nur Platzhalterbild → kein Foto")
        flags.append("keine GTIN publiziert")
        prot = n.get("protein"); kcal = n.get("kcal")
        pp = round(prot * size / 100, 1) if prot is not None and size else ""
        kp = round(kcal * size / 100) if kcal is not None and size else ""
        rows.append({"name": d["name"], "brand": "Flotte Lotte", "store": M.STORE, "price_eur": d["price_eur"], "size_g": size or "",
             "price_per_kg": d["unit_price_eur"] or "", "url": d["source_url"], "image_url": d["image_url"] or "",
             "kcal_100": kcal if kcal is not None else "", "protein_100": prot if prot is not None else "",
             "fat_100": n.get("fat", ""), "satfat_100": n.get("satfat", ""), "carbs_100": n.get("carbs", ""),
             "sugar_100": n.get("sugar", ""), "fiber_100": n.get("fiber", ""), "salt_100": n.get("salt", ""),
             "protein_pack": pp, "kcal_pack": kp,
             "eur_per_10g_protein": round(d["price_eur"] / (pp / 10), 2) if pp else "",
             "manufacturer": "Flotte Lotte GmbH (Zwettl)", "producer_id": "flotte-lotte", "origin": "AT (Niederösterreich, Zwettl)",
             "bio": False, "veg": True, "prep": "im Topf erwärmen", "category": "Online Meal-Prep",
             "price_source": f"flottelottezwettl.at Produktseite {day} (inkl. 10 % USt., zzgl. Versand); {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "flottelottezwettl.at Produktseite je 100 g" if n else "",
             "packaging": "Glas", "online": True, "available": x["in_stock"], "storage": x["storage"] or "",
             "shelf_life": "", "shipping_eur": M.SHIPPING_AT, "nut_flag": "; ".join(flags), "ean": "", "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://flottelottezwettl.at/{Eintoepfe,Suppen} + product pages (JTL-Shop, 1 req/s)", "fetched": stamp,
           "robots": "robots.txt: User-agent: * / Disallow: (empty = all allowed)",
           "operator": "Flotte Lotte GmbH", "fn": "FN 550284 t (LG Krems an der Donau, per Impressum)",
           "impressum": {"https://flottelottezwettl.at/Impressum": "Flotte Lotte GmbH, Pater Werner Deibl Strasse 5, 3910 Zwettl; Firmenbuchnummer 550284 t, LG Krems an der Donau; Unternehmensgegenstand Lebensmittelherstellung; UID ATU76539079; GLN 9110029937544; GISA 33497105"},
           "vies": {"uid": "ATU76539079", "valid": True, "checked": "2026-10-25T09:12:30Z", "name": "Flotte Lotte GmbH", "address": "Pater Werner Deibl-Straße 5, AT-3910 Zwettl-NÖ"},
           "gleif": "legalName filter 'Flotte Lotte' → 0 records → no LEI",
           "shipping": {"https://flottelottezwettl.at/Versandinformationen": "Versand Di–Do per Expressversand gekühlt; AT DHL, DE Go Express; AT kostenlos ab 100 €, 75–99,99 € 7,90 €, darunter 9,90 €; DE 17,90 € (75–149,99 €) bzw. 19,90 €"},
           "note": "legacy WooCommerce shop under /wp/ (same products, no nutrition) not used; JTL shop is current",
           "photo_vision_gate": "13/13 PASS (Flotte Lotte jar labels match product names and 380 g / 380 ml); Pastinaken Apfel Suppe + Schwarzwurzel Suppe show only the shop placeholder keinBild.gif → no photo",
           "excluded": ["Sugos (alla Norma, Veganese, Zucchini) = pasta sauces", "Chutneys", "Fruchtaufstriche", "Fruchtmus", "Röster",
                        "Sonstiges (Suppengewürz, Paprika Ananas Grillsauce, Zucchini Tomaten Brotaufstrich)", "Probier-/Geschenksets, Baumpatenschaften"],
           "existing_rows": "OFF row Fenchel Kartoffel Suppe EAN 9120113491784 (products.csv) = same product → dedupe candidate; logo flotte-lotte already in logos.csv",
           "kept": kept}
    json.dump(out, open(f"raw/flottelotte_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "flotte-lotte"]
    ap = sorted(r["price_eur"] for r in rows); ep = sorted(r["eur_per_10g_protein"] for r in rows if r["eur_per_10g_protein"] != "")
    comp.append({c: "" for c in ccols} | {"slug": "flotte-lotte", "name": "Flotte Lotte", "role": "producer+retailer",
        "legal_name": "Flotte Lotte GmbH", "fn": "FN 550284t", "register_id": "FN 550284t", "register_authority": "Firmenbuch",
        "legal_form_code": "GmbH", "country": "AT", "address": "Pater Werner Deibl-Straße 5, AT-3910 Zwettl", "entity_status": "UID VIES gültig; kein LEI",
        "website": "https://flottelottezwettl.at", "product_count": len(rows), "median_price_eur": ap[len(ap) // 2],
        "median_eur_per_10g_protein": ep[len(ep) // 2] if ep else "", "fetched_at": stamp,
        "brands": "Flotte Lotte", "chains": M.STORE, "uid": "ATU76539079", "uid_vies_name": "Flotte Lotte GmbH",
        "uid_vies_address": "Pater Werner Deibl-Straße 5, AT-3910 Zwettl-NÖ", "uid_checked_at": "2026-10-25T09:12Z",
        "imprint_url": "https://flottelottezwettl.at/Impressum", "register_court": "LG Krems an der Donau", "registry_status": "fn_from_impressum_uid_vies_valid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
