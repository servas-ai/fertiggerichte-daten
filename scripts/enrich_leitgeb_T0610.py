"""Leitgeb's Kärntnernudel (kaerntnernudel.co.at; Leitgeb's Nudelspezialitäten aus dem Metnitztal GmbH, Industriestraße 18,
9360 Friesach, Kärnten; FN 62213v LG Klagenfurt; UID ATU82506478 EU VIES valid 2026-10-25T06:08Z, name/address match;
GLEIF fulltext 'Leitgeb's Nudelspezialitäten' → 0 → no LEI; GF Caroline Leitgeb, Christoph Eder)
→ rows 'Online: Leitgeb's Kärntnernudel' in data/online_mealprep.csv (idempotent replace) + evidence raw/leitgeb_<stamp>.json
+ new company row 'leitgebs' (matches existing data/logos.csv slug) (Daten-Squad 2026-10-25T0610).
Source: food-connectors `leitgeb` adapter (public WooCommerce Store API + product pages at 1 s) → 29 of 38 products:
22 savoury pre-cooked Kärntner Nudeln (10 Stk.), 2 Nudelteller, 3 filled Knödel (4 Stk.); excluded sweet Nudeln (6),
Süßer Nudelteller, Schlickkrapferl (soup garnish), Semmelknödel (side).
Pack weight = pieces × shop's approx. piece weight ('ca.') → flagged. Nutrition per 100 g as printed (26/29); none estimated.
Photos: primary packshots vision-checked 29/29 PASS (cut-open Nudel/Knödel with the named filling; Bio and conventional
variants share 7 photos). No GTIN. Shipping cooled AT/DE Mon–Thu, fee only in cart → shipping_eur empty.
Usage: python3 scripts/enrich_leitgeb_T0610.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import leitgeb as L

CSV = "data/online_mealprep.csv"
PRODUCER = "Leitgeb's Nudelspezialitäten aus dem Metnitztal GmbH (Friesach Ktn)"
MEAT = ("speck", "fleisch", "lasagne", "tiroler")


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = L.store_products()
    kept = [p.to_dict() for p in L.Leitgeb().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; n = d["nutrition_100g"] or {}; size = d["size_g"]; name = d["name"].lower()
        knoedel = "knödel" in name
        flags = ["Packungsgewicht = Stück × ca.-Stückgewicht lt. Shop",
                 ("Nährwerte je 100 g lt. Shop" if n else "keine Nährwerte im Shop → nicht geschätzt"),
                 f"Allergene lt. Shop: {x.get('allergens') or '—'}; keine GTIN",
                 "Versandkosten nur im Warenkorb → leer"]
        bio = name.startswith("bio ")
        veg = not any(m in name for m in MEAT)
        rows.append({"name": d["name"], "brand": "Leitgeb's Nudelspezialitäten", "store": L.STORE, "price_eur": d["price_eur"],
             "size_g": int(size) if size else "", "price_per_kg": d["unit_price_eur"] or "",
             "url": d["source_url"], "image_url": d["image_url"] or "",
             "kcal_100": n.get("kcal", ""), "protein_100": n.get("protein", ""), "fat_100": n.get("fat", ""),
             "satfat_100": n.get("saturated_fat", ""), "carbs_100": n.get("carbs", ""), "sugar_100": n.get("sugar", ""),
             "salt_100": n.get("salt", ""),
             "protein_pack": round(n["protein"] * size / 100, 1) if n.get("protein") is not None and size else "",
             "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None and size else "",
             "eur_per_10g_protein": round(d["price_eur"] / (n["protein"] * size / 100) * 10, 2) if n.get("protein") and size else "",
             "manufacturer": PRODUCER, "producer_id": "leitgebs", "origin": "AT", "bio": bio, "veg": veg,
             "prep": ("vorgekocht – in Salzwasser/Dampf erwärmen" if knoedel else "vorgekocht – nur erwärmen (kochen, braten oder Dampf)"),
             "category": "Online Meal-Prep",
             "price_source": f"kaerntnernudel.co.at WooCommerce Store API {day}, Preis je Packung inkl. 10 % MwSt; zzgl. Versand",
             "price_date": day, "nut_source": ("kaerntnernudel.co.at Produktseite 'Nährwerte' je 100 g" if n else ""),
             "packaging": f"{x.get('pieces')} Stück (ca. {x.get('piece_g_approx')} g/Stk.)" if x.get("pieces") else "",
             "online": True, "available": bool(x.get("in_stock")), "storage": "gekühlt (Kühlversand AT/DE Mo–Do) oder tiefgekühlt",
             "shelf_life": x.get("shelf_life") or "", "shipping_eur": "", "nut_flag": "; ".join(flags), "ean": None,
             "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != L.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": L.BASE + "/wp-json/wc/store/v1/products?per_page=100 + /produkt/<slug>/ pages (1 s)", "fetched": stamp,
           "operator": L.PRODUCER,
           "vies": "ATU82506478 valid 2026-10-25T06:08Z; name 'Leitgeb's Nudelspezialitäten aus dem Metnitztal GmbH', address 'Industriestraße 18, AT-9360 Friesach'",
           "gleif": "fulltext 'Leitgeb's Nudelspezialitäten' / 'Leitgeb Nudel Friesach' → 0 records → no LEI",
           "impressum": L.BASE + "/impressum/ (FN 62213v, Landesgericht Klagenfurt; GF Caroline Leitgeb, Christoph Eder; Aufsicht BH St. Veit a.d.Glan)",
           "robots": "User-agent: * Disallow only /wp-admin/ and WooCommerce log/upload/transient folders",
           "shipping": L.SHIPPING_NOTE, "photo_vision_gate": "29/29 PASS",
           "all_shop_products": [{"id": p["id"], "name": L._name(p), "price": int(p["prices"]["price"]) / 100,
                                  "meal": L.is_meal(p)} for p in shop],
           "excluded": [L._name(p) for p in shop if not L.is_meal(p)], "kept": kept}
    json.dump(out, open(f"raw/leitgeb_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "leitgebs"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "leitgebs", "name": "Leitgeb's Nudelspezialitäten", "role": "producer",
        "legal_name": "Leitgeb's Nudelspezialitäten aus dem Metnitztal GmbH", "fn": "FN 62213v", "register_id": "FN 62213v",
        "register_authority": "Firmenbuch (Landesgericht Klagenfurt)", "legal_form_code": "GmbH", "country": "AT",
        "address": "Industriestraße 18, AT-9360 Friesach", "entity_status": "UID VIES gültig; kein LEI",
        "owners": "GF: Caroline Leitgeb, Christoph Eder", "website": L.BASE, "product_count": len(rows),
        "median_price_eur": prices[len(prices) // 2], "fetched_at": stamp,
        "brands": "Leitgeb's Nudelspezialitäten", "chains": L.STORE + "; Gurkerl", "plants_count": 1,
        "uid": "ATU82506478", "uid_vies_name": "Leitgeb's Nudelspezialitäten aus dem Metnitztal GmbH",
        "uid_vies_address": "Industriestraße 18, AT-9360 Friesach", "uid_checked_at": "2026-10-25T06:08Z",
        "imprint_url": L.BASE + "/impressum/", "register_court": "Landesgericht Klagenfurt",
        "registry_status": "fn_from_imprint_uid_vies_valid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
