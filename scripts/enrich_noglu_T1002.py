"""NoGlu — glutenfreie Knödel-Manufaktur (noglu.at, WooCommerce; Andreas Rossmeier, Einzelunternehmen, Ziegelweg 10,
6060 Hall in Tirol, Tirol; no Firmenbuch entry, GISA 35944898; UID ATU62240088 VIES valid 2026-10-25 as
'Rossmeier Andreas Markus'; GLEIF no LEI) — 4 gluten- and lactose-free, fully cooked, vacuum-packed frozen Knödel ready meals.
Source: food-connectors `noglu` (WooCommerce Store API, 1 request → price incl. MwSt., 4 × 125 g, stock, packshot,
Nährwerte per 100 g from the description table). Photos vision-checked 4/4 distinct real dish photos.
No ingredients or GTIN published → empty, never estimated. Shipping: frozen thermo carton, Wednesdays, AT 16,90 € / DE 25,90 €
per carton (≤28 packs). Excluded: Semmelknödel (plain side), Probiersortiment/Familienbox/Vorratsbox (bundles of the same packs).
Usage: python3 scripts/enrich_noglu_T1002.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import noglu as M

CSV = "data/online_mealprep.csv"
SLUG = "noglu"
VEG = {"KN-SPINAT": True, "KN-SPECK": False}  # Spinatknödel 'die feine vegetarische Variante' lt. Shop; Käse-Sorten nicht deklariert → leer


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    sigs = {}
    for d in kept:
        sigs.setdefault(tuple(sorted((d["nutrition_100g"] or {}).items())), []).append(d["name"])
    rows = []
    for d in kept:
        x = d["extra"]; n = d["nutrition_100g"] or {}; size = d["size_g"]
        flags = ["Preis inkl. MwSt. lt. Produktseite (WooCommerce Store API)",
                 "Nährwerte je 100 g lt. Produktseite (lt. Shop bezogen auf die Rezeptur vor dem Kochen)"]
        twins = [o for o in sigs[tuple(sorted(n.items()))] if o != d["name"]]
        if n and twins:
            flags.append("identische Nährwerte wie " + ", ".join(twins) + " – wie publiziert")
        if n.get("kcal") is not None and all(n.get(k) is not None for k in ("fat", "carbs", "protein")):
            at = 9 * n["fat"] + 4 * n["carbs"] + 4 * n["protein"] + 2 * (n.get("fiber") or 0)
            if abs(at - n["kcal"]) > max(8, 0.25 * n["kcal"]):
                flags.append(f"Atwater {at:.0f} kcal vs. deklariert {n['kcal']:g} kcal")
        flags += ["keine Zutatenliste publiziert", "keine GTIN publiziert", f"Packung {x['pieces']} Stück à {x['piece_g']:g} g"]
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
             "manufacturer": "NoGlu – Andreas Rossmeier (Einzelunternehmen), Ziegelweg 10, 6060 Hall in Tirol (UID ATU62240088)",
             "producer_id": SLUG, "origin": "AT (Tirol, Hall in Tirol, eigene Manufaktur)",
             "bio": False, "veg": VEG.get(x["sku"], ""), "prep": "fertig gegart, tiefgekühlt, vakuumverpackt; nur erhitzen (lt. Shop)",
             "category": "Online Meal-Prep",
             "price_source": f"noglu.at WooCommerce Store API {day} (inkl. MwSt., zzgl. Versand); {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "noglu.at Produktseite Nährwerttabelle je 100 g" if n else "",
             "packaging": "Vakuumbeutel", "online": True, "available": x["in_stock"],
             "storage": "tiefgekühlt (aufgetaut im Kühlschrank ca. 10 Tage lt. Versandseite)", "shelf_life": "",
             "shipping_eur": M.SHIPPING_AT, "nut_flag": "; ".join(flags), "ean": "", "portions": x["pieces"] or ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.noglu.at/wp-json/wc/store/v1/products?per_page=100 (1 request)",
           "fetched": stamp,
           "robots": "robots.txt (www.noglu.at) disallows only /wp-admin/, cart/warenkorb, checkout/kasse, my-account/mein-konto, ?wc-ajax/?add-to-cart/?orderby and WC log/upload folders",
           "operator": "Andreas Rossmeier (Einzelunternehmen)", "fn": "keine Firmenbuchnummer (Einzelunternehmen, nicht protokolliert); GISA-Zahl 35944898",
           "impressum": {"https://www.noglu.at/impressum/":
                         "Andreas Rossmeier, Einzelunternehmen, Ziegelweg 10, 6060 Hall in Tirol; Tel +43 699 16226510; info@noglu.at; UID ATU62240088; GISA-Zahl 35944898; Unternehmensgegenstand Erzeugung und Handel mit Lebensmitteln; WK Tirol Mitgliedsnummer 9110011469411; Gewerbebehörde BH Innsbruck; auch: Andis Grillwelt, MONOLITH Keramikgrills"},
           "vies": {"uid": "ATU62240088", "valid": True, "checked": "2026-10-25T10:04:07Z", "name": "Rossmeier Andreas Markus", "address": "Ziegelweg 10, AT-6060 Hall in Tirol"},
           "gleif": "fulltext 'Rossmeier' → 0 records; fulltext 'NoGlu' → 0 records → no LEI",
           "shipping": {"https://www.noglu.at/versand/": "Lieferung nach Österreich und Deutschland; Thermokarton bis 14 kg = 28 Packungen; AT 16,90 € / DE 25,90 € je Karton; Versand mittwochs, Bestellungen bis Di 12 Uhr; AT meist am nächsten Tag; tiefgefroren, fertig gegart und vakuumverpackt"},
           "photo_vision_gate": "4/4 PASS — distinct real dish photos (Kasnocken with Käse/Schnittlauch, angebratener Kaspressknödel, aufgeschnittene Speckknödel, Spinatknödel mit Parmesan); no placeholders",
           "excluded": ["Glutenfreie Semmelknödel 4 Stück (500 g) 9,00 € = Beilage", "NoGlu Probiersortiment 5 Sorten (2,5 kg) 45,00 € = Bundle",
                        "NoGlu Familienbox 8 Packungen (4 kg) 69,00 € = Bundle", "NoGlu Vorratsbox 10 Packungen (5 kg) 85,00 € = Bundle"],
           "notes": ["Kaspressknödel und Kasnocken mit identischen Nährwerten publiziert", "keine Zutaten/GTIN im Shop"],
           "kept": kept}
    json.dump(out, open(f"raw/noglu_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != SLUG]
    ap = sorted(r["price_eur"] for r in rows); ep = sorted(r["eur_per_10g_protein"] for r in rows if r["eur_per_10g_protein"] != "")
    comp.append({c: "" for c in ccols} | {"slug": SLUG, "name": "NoGlu (glutenfreie Knödel-Manufaktur)", "role": "producer+retailer",
        "legal_name": "Andreas Rossmeier (Einzelunternehmen)", "legal_form_code": "Einzelunternehmen", "country": "AT",
        "address": "Ziegelweg 10, AT-6060 Hall in Tirol", "entity_status": "UID VIES gültig; kein Firmenbuch (Einzelunternehmen, GISA 35944898); kein LEI",
        "owners": "Andreas Rossmeier lt. Impressum", "website": "https://www.noglu.at", "product_count": len(rows),
        "median_price_eur": ap[len(ap) // 2], "median_eur_per_10g_protein": ep[len(ep) // 2] if ep else "", "fetched_at": stamp,
        "brands": "NoGlu", "chains": M.STORE, "plants_count": 1, "uid": "ATU62240088",
        "uid_vies_name": "Rossmeier Andreas Markus", "uid_vies_address": "Ziegelweg 10, AT-6060 Hall in Tirol", "uid_checked_at": "2026-10-25T10:04Z",
        "imprint_url": "https://www.noglu.at/impressum/", "registry_status": "imprint_uid_vies_valid_no_fn"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
