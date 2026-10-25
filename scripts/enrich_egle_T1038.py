"""Egle (egleshop.at, Shopware 6; Wilhelm Egle GmbH, Runastraße 3, 6800 Feldkirch — Austrian office of the German GmbH,
HRB 6630 Registergericht Memmingen, USt-IdNr. DE130855821 VIES valid 2026-10-25 (name/address not disclosed by DE),
no Austrian FN, GLEIF no LEI) — 31 shelf-stable canned/jarred ready meals & soups, mostly BIO, Austria-only delivery.
Source: food-connectors `egle` (category pages + product pages, 1 req/s: price incl. MwSt., Inhalt, Zutaten, Nährwerte per
100 g, F01 packshot, stock). Photos vision-checked 31/31 real packshots. No GTIN published → empty.
Packaging: 'Dose'/'Glas' from the Zubereitung text; where the text does not say, from the vision-checked packshot (marked).
Excluded: 2 x / 3 x / Sparpaket multipacks, fish preserves, Sauce Bolognese, dry mixes (Risotto, Bulgurpfanne, Veg. Hack,
Püree, Bratlinge, Pancakes, Graupen-/Zwiebelsuppe, Figur-Balance, Brühen/Delikatess-Suppe), Wild-Preiselbeeren.
Usage: python3 scripts/enrich_egle_T1038.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import egle as M

CSV = "data/online_mealprep.csv"
SLUG = "egle"
PHOTO_PACK = {"120": "Glas", "110177": "Glas", "110178": "Glas", "156": "Glas", "274": "Glas", "755": "Glas",
              "132": "Dose", "160": "Dose", "161": "Dose"}
VEG = {"110178", "755", "274", "110183", "110184"}  # shop category 'Vegetarische Fertiggerichte'


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        x = d["extra"]; n = d["nutrition_100g"] or {}; size = d["size_g"]; sku = d["source_id"]
        flags = ["Preis inkl. MwSt. lt. Produktseite", "Nährwerte je 100 g lt. Produktseite"]
        if n.get("kcal") is not None and all(n.get(k) is not None for k in ("fat", "carbs", "protein")):
            at = 9 * n["fat"] + 4 * n["carbs"] + 4 * n["protein"] + 2 * (n.get("fiber") or 0)
            if abs(at - n["kcal"]) > max(8, 0.25 * n["kcal"]):
                flags.append(f"Atwater {at:.0f} kcal vs. deklariert {n['kcal']:g} kcal")
        pack = x["packaging"]
        if not pack and sku in PHOTO_PACK:
            pack = PHOTO_PACK[sku]; flags.append(f"Verpackung {pack} lt. Produktfoto")
        if x["size_unit"] == "ml":
            flags.append("Inhalt in ml lt. Shop, size_g = ml-Angabe")
        if "Wasser zufügen" in (x["prep"] or ""):
            flags.append("Zubereitung mit Wasserzugabe lt. Shop (" + x["prep"][:90] + ")")
        if not x["in_stock"]:
            flags.append(f"momentan nicht lieferbar lt. Shop {day}")
        flags.append("keine GTIN publiziert")
        prot = n.get("protein"); kcal = n.get("kcal")
        pp = round(prot * size / 100, 1) if prot is not None and size else ""
        kp = round(kcal * size / 100) if kcal is not None and size else ""
        rows.append({"name": d["name"], "brand": M.BRAND, "store": M.STORE, "price_eur": d["price_eur"], "size_g": size or "",
             "price_per_kg": d["unit_price_eur"] or "", "url": d["source_url"], "image_url": d["image_url"] or "",
             "kcal_100": kcal if kcal is not None else "", "protein_100": prot if prot is not None else "",
             "fat_100": n.get("fat", ""), "satfat_100": n.get("satfat", ""), "carbs_100": n.get("carbs", ""),
             "sugar_100": n.get("sugar", ""), "fiber_100": n.get("fiber", ""), "salt_100": n.get("salt", ""),
             "protein_pack": pp, "kcal_pack": kp,
             "eur_per_10g_protein": round(d["price_eur"] / (pp / 10), 2) if pp else "",
             "manufacturer": M.OPERATOR, "producer_id": SLUG,
             "origin": "DE (Produktionsland lt. Shop)" if d["origin"] == "Deutschland" else "",
             "bio": bool(x["bio"]), "veg": True if sku in VEG else False,
             "prep": ("Konserve; " + x["prep"]) if x["prep"] else "Konserve; nur erhitzen",
             "category": "Online Meal-Prep",
             "price_source": f"egleshop.at Produktseite {day} (inkl. MwSt., zzgl. Versand); {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "egleshop.at Produktseite Nährwerttabelle je 100 g" if n else "",
             "packaging": pack or "", "online": True, "available": bool(x["in_stock"]),
             "storage": "ungekühlt (Konserve)", "shelf_life": "",
             "shipping_eur": M.SHIPPING_AT, "nut_flag": "; ".join(flags), "ean": "", "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.egleshop.at/Lebensmittel/Fertiggerichte-Fisch/ + /Lebensmittel/Suppen-Sossen/Eintoepfe/ → product pages (1 req/s)",
           "fetched": stamp, "robots": "https://www.egleshop.at/robots.txt → HTTP 404 (no rules)",
           "operator": "Wilhelm Egle GmbH (deutsche GmbH; österreichische Niederlassung Feldkirch)",
           "fn": "keine österreichische Firmenbuchnummer im Impressum; HRB 6630, Registergericht Memmingen",
           "impressum": {"https://www.egleshop.at/Impressum/":
                         "Wilhelm Egle GmbH, Runastraße 3, 6800 Feldkirch; Geschäftsführer Carsten Rocholl; Registergericht Memmingen HRB 6630; Gerichtsstand Neu-Ulm; USt-IdNr. DE130855821; Öko-Kontrollstelle DE-ÖKO-001"},
           "vies": {"uid": "DE130855821", "valid": True, "checked": "2026-10-25", "name": "---", "address": "---"},
           "gleif": "legalName 'Wilhelm Egle GmbH' / fulltext 'Egle' → no matching record → no LEI",
           "shipping": {"https://www.egleshop.at/Lieferung/": "Die Lieferung erfolgt nur innerhalb Österreichs; Mindestbestellwert 25 €; Versandkosten 4,95 €, ab 75 € versandkostenfrei; Lieferzeit 5–7 Werktage"},
           "photo_vision_gate": "31/31 PASS — real Egle F01 packshots (cans/jars with dish photo); no placeholders",
           "excluded": ["all '2 x' / '3 x' / Sparpaket multipacks = Bundles", "fish preserves (Thunfisch, Heringsfilets, Makrelen, Lachsfilets, Forellen-/Bücklingsfilets, Lachspastete, Lachs-/Thunfischsalat, Bratheringsfilets) = keine Fertiggerichte",
                        "BIO Sauce Bolognese = Sauce", "BIO Wild-Preiselbeeren = Beilage",
                        "dry mixes: Steinpilz-Risotto 300 g (404 kcal/100 g), BIO Bulgurpfanne, BIO Vegetarisches Hack, BIO Kartoffel-Püree, BIO Grünkern-Bratlinge, BIO Pancakes-Mischung",
                        "Suppen-Trockenmischungen/Brühen: BIO Bündner Graupensuppe, BIO Zwiebelsuppe, Figur-Balance Gemüse-/Kartoffelsuppe, Delikatess-Suppe, Klare Delikatess-Suppe, Klare Gemüsebrühe, BIO Klare Brühe und Würze, BIO Salzarme Gemüse-Bouillon"],
           "notes": ["Betreiber ist eine deutsche GmbH, der Shop liefert aber ausschließlich innerhalb Österreichs",
                     "BIO Traditionelle Maultaschen: 400 ml Dose + 300 ml Wasser lt. Zubereitung",
                     "BIO Veganes Gulasch und BIO Käsenockerl-Suppe am Abruftag 'momentan nicht lieferbar'"],
           "kept": kept}
    json.dump(out, open(f"raw/egle_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != SLUG]
    ap = sorted(r["price_eur"] for r in rows); ep = sorted(r["eur_per_10g_protein"] for r in rows if r["eur_per_10g_protein"] != "")
    comp.append({c: "" for c in ccols} | {"slug": SLUG, "name": "Egle (egleshop.at)", "role": "producer+retailer",
        "legal_name": "Wilhelm Egle GmbH", "legal_form_code": "GmbH (DE)", "country": "DE",
        "address": "Runastraße 3, AT-6800 Feldkirch (österreichische Niederlassung lt. Impressum)",
        "entity_status": "USt-IdNr. VIES gültig; HRB 6630 AG Memmingen; keine AT-FN; kein LEI",
        "owners": "", "website": "https://www.egleshop.at", "product_count": len(rows),
        "median_price_eur": ap[len(ap) // 2], "median_eur_per_10g_protein": ep[len(ep) // 2] if ep else "", "fetched_at": stamp,
        "brands": "Egle", "chains": M.STORE, "uid": "DE130855821",
        "uid_vies_name": "---", "uid_vies_address": "---", "uid_checked_at": "2026-10-25",
        "imprint_url": "https://www.egleshop.at/Impressum/", "register_court": "Amtsgericht Memmingen", "hrb": "HRB 6630",
        "registry_status": "imprint_uid_vies_valid_de_hrb_no_at_fn"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
