"""zoart — Sous Vide Fertiggerichte vom Schwein (sous-vide-fertiggerichte.at, also zoart.at; Barbara Fink KG, Oberrettenbach 19,
8212 Gersdorf an der Feistritz, Steiermark; FN 431088 d LG für ZRS Graz per Impressum; UID ATU69421556 VIES valid 2026-10-25;
GLEIF no LEI) — 19 sous-vide pre-cooked Styrian pork ready meals (15 products, weight variants as separate rows).
Source: food-connectors `zoart` (WooCommerce Store API + variation endpoints → price incl. 10 % MwSt., pack size, stock, packshot).
Photos vision-checked 15/15 distinct real dish photos. No nutrition, ingredients or GTIN published → empty, never estimated.
Shipping: chilled Post within 24 h, 12 € below 100 €, free from 100 €. Excluded: Bratensaft/Jus (sauce), Zunge (Jause/Vorspeise).
Usage: python3 scripts/enrich_zoart_T0935.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import zoart as M

CSV = "data/online_mealprep.csv"
SLUG = "barbara-fink-kg"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]
        flags = ["Preis inkl. 10 % MwSt., inkl. Verpackung lt. Produktseite (WooCommerce Store API)",
                 "keine Nährwerte/Zutaten publiziert", "keine GTIN publiziert"]
        if x["variant"]:
            flags.append(f"Gewichtsvariante {x['variant']} (Variation {x['variation_id']}) als eigene Zeile")
        if x["size_unit"] == "ml":
            flags.append(f"Gesamtmenge 700 ml davon {x['meat_g']:g} g Fleisch – ml als g übernommen")
        if x["pieces_note"]:
            flags.append(f"Packung: {x['pieces_note']}")
        rows.append({"name": d["name"], "brand": M.BRAND, "store": M.STORE, "price_eur": d["price_eur"], "size_g": size or "",
             "price_per_kg": d["unit_price_eur"] or "", "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": "Barbara Fink KG (zoart), Oberrettenbach 19, 8212 Gersdorf an der Feistritz (FN 431088 d, UID ATU69421556)",
             "producer_id": SLUG, "origin": "AT (Steiermark, Schweinefleisch lt. Shop; Betrieb mit eigener Schweinemast)",
             "bio": False, "veg": False, "prep": x["prep"], "category": "Online Meal-Prep",
             "price_source": f"sous-vide-fertiggerichte.at WooCommerce Store API {day} (inkl. 10 % MwSt., zzgl. Versand); {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "", "packaging": x["packaging"], "online": True, "available": x["in_stock"],
             "storage": "gekühlt (Versand im Naturkarton mit Icepacks)", "shelf_life": "", "shipping_eur": M.SHIPPING_AT,
             "nut_flag": "; ".join(flags), "ean": "", "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.sous-vide-fertiggerichte.at/wp-json/wc/store/v1/products?per_page=100 + /products/<variation id> (1 req/s)",
           "fetched": stamp,
           "robots": "robots.txt disallows only /wp-content/uploads/wc-logs/, woocommerce_transient_files/, woocommerce_uploads/, /wp-admin/",
           "operator": "Barbara Fink KG", "fn": "FN 431088 d (Landesgericht für ZRS Graz, per Impressum)",
           "impressum": {"https://www.sous-vide-fertiggerichte.at/impressum-sous-vide-fertiggerichte-barbara-fink-kg/":
                         "Betreiber des Onlineshops sous-vide-fertiggerichte.at, auch erreichbar unter zoart.at: Barbara Fink KG, Oberrettenbach 19, 8212 Gersdorf an der Feistritz; Unternehmensgegenstand Schweinemast und Ackerbau; UID ATU69421556; FN 431088 d, LG für ZRS Graz; Komplementärin Barbara Fink, Kommanditist Christoph Fink"},
           "vies": {"uid": "ATU69421556", "valid": True, "checked": "2026-10-25T09:40:14Z", "name": "Barbara Fink KG", "address": "Oberrettenbach 19, AT-8213 Gersdorf/Feistritz"},
           "gleif": "fulltext 'Barbara Fink' → only unrelated CH record; registeredAs 431088d → 0 records → no LEI",
           "shipping": {"https://www.sous-vide-fertiggerichte.at/verpackung-versand/": "Naturkarton foodmailer, Icepacks aus Papier, Zustellung innerhalb 24 h durch die Österreichische Post; ab 100 € kostenlos, darunter 12,00 €; Abholung Rosy's Abholstationen"},
           "photo_vision_gate": "15/15 PASS — each product has its own real dish photo (Rouladen, Gulasch-Glas, Stelzen, Pulled-Pork-Burger, Bauch, Braten, Spareribs, Steaks, Wangerl, Fischerl); no md5 duplicates, no placeholders",
           "excluded": ["Bratensaft/Jus im Glas 240 ml 6,50 € = Sauce", "Zunge 380 g 14,30 € = als Vorspeise/Jause beworben (Aufschnitt)"],
           "kept": kept}
    json.dump(out, open(f"raw/zoart_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != SLUG]
    ap = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": SLUG, "name": "zoart Sous Vide Fertiggerichte (Barbara Fink KG)", "role": "producer+retailer",
        "legal_name": "Barbara Fink KG", "fn": "FN 431088d", "register_id": "FN 431088d", "register_authority": "Firmenbuch",
        "legal_form_code": "KG", "country": "AT", "address": "Oberrettenbach 19, AT-8212 Gersdorf an der Feistritz", "entity_status": "UID VIES gültig; kein LEI",
        "owners": "Barbara Fink (Komplementärin), Christoph Fink (Kommanditist) lt. Impressum",
        "website": "https://www.sous-vide-fertiggerichte.at", "product_count": len(rows), "median_price_eur": ap[len(ap) // 2],
        "median_eur_per_10g_protein": "", "fetched_at": stamp, "brands": "zoart Sous Vide", "chains": M.STORE, "uid": "ATU69421556",
        "uid_vies_name": "Barbara Fink KG", "uid_vies_address": "Oberrettenbach 19, AT-8213 Gersdorf/Feistritz", "uid_checked_at": "2026-10-25T09:40Z",
        "imprint_url": "https://www.sous-vide-fertiggerichte.at/impressum-sous-vide-fertiggerichte-barbara-fink-kg/",
        "register_court": "Landesgericht für ZRS Graz", "registry_status": "fn_from_impressum_uid_vies_valid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
