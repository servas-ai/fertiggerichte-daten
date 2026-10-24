"""Wiesbauer Gourmet own webshop (wiesbauer-gourmet.at, Wiesbauer Gourmet Gastro GmbH, Reidling NÖ) → rows
'Online: Wiesbauer Gourmet' in data/online_mealprep.csv (idempotent replace) + evidence raw/wiesbauer_gourmet_<stamp>.json
(Daten-Squad 2026-10-24T2111). Company (FN 98447a, UID ATU20162703 VIES valid 2026-10-24) and logo already present.
Source: food-connectors `wiesbauer_gourmet` adapter (public WooCommerce Store API, robots disallow only /wp-admin/),
categories easy-kitchen / sous-vide / wirtshauskultur-fuer-daheim. Kept 20 pre-cooked heat-up dishes/mains; excluded
sauces/jus, sides, bundles, raw meat, Würstel, breaded frozen raw schnitzel, Pulled Pork (burger filling), 2 kg Roastbeef.
Nutrition only where the shop prints it per 100 g; Kalbs Tafelspitz prints 375 kJ / 388 kcal (contradictory) → left empty.
'< 0,5 g' values are recorded as 0.5 and flagged. No GTIN published (SKU only) → ean empty.
Photos: first image per product, vision gate 20/20 PASS (scripts/logo_work_T2111/wiesbauer_gourmet_photo_sheet.jpg).
Shipping: AT/DE only, 19,90 € up to 149 €, free from 150 € (Versand page + AGB §5)."""
import sys, json, csv, datetime, re
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import wiesbauer_gourmet as W

CSV = "data/online_mealprep.csv"


def origin(name):
    if "USA" in name:
        return "Fleisch USA lt. Produktname; Verarbeitung AT (Reidling NÖ)"
    if "Österreich" in name:
        return "Fleisch AT lt. Produktname; Verarbeitung AT (Reidling NÖ)"
    return "Verarbeitung AT (Reidling NÖ); Fleischherkunft nicht angegeben"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = W.store_products()
    kept = [W.to_product(sp).to_dict() for sp in shop if W.is_meal(sp)]
    excluded = [{"id": sp["id"], "slug": sp["slug"], "name": sp["name"]} for sp in shop if not W.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; price = d["price_eur"]; n = d["nutrition_100g"] or {}
        pp = round(n["protein"] * size / 100, 1) if n.get("protein") and size else None
        m = re.search(r"für (\d+) Person", x["description"])
        flags = ["keine GTIN veröffentlicht (nur SKU " + str(x.get("sku")) + ")"]
        if x.get("nut_flag") == "shop_kj_kcal_inconsistent":
            flags.append("Shop-Nährwerte widersprüchlich (kJ/kcal) → nicht übernommen")
        elif x.get("nut_flag"):
            flags.append("'< 0,5 g' als 0.5 erfasst")
        if not n and not x.get("nut_flag"):
            flags.append("keine Nährwerte veröffentlicht → nicht geschätzt")
        if re.search(r"Stelze|Knochen|Spareribs|Drumsticks|Shortribs|halbiert", d["name"]):
            flags.append("Gewicht inkl. Knochen")
        rows.append({"name": d["name"], "brand": d["brand"], "store": W.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2) if size else None, "url": d["source_url"], "image_url": d["image_url"],
            "kcal_100": n.get("kcal"), "protein_100": n.get("protein"), "fat_100": n.get("fat"), "satfat_100": n.get("saturated_fat"),
            "carbs_100": n.get("carbs"), "sugar_100": n.get("sugar"), "salt_100": n.get("salt"),
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") and size else None,
            "eur_per_10g_protein": round(price / pp * 10, 2) if pp else None,
            "manufacturer": W.PRODUCER, "origin": origin(d["name"]), "bio": False, "veg": False,
            "prep": ("vorgegart, im Topf erwärmen (lt. Produktseite)" if x["line"] == "Easy Kitchen"
                     else "sous vide vorgegart, im Backrohr/Wasserbad erwärmen (lt. Produktseite)"),
            "category": "Online Meal-Prep",
            "price_source": f"wiesbauer-gourmet.at WooCommerce Store API Preis/Packung {day} (zzgl. 19,90 € Versand unter 150 €)",
            "price_date": day, "nut_source": d["source_url"] if n else None, "packaging": f"Vakuumbeutel {int(size)} g" if size else "Vakuumbeutel",
            "online": True, "available": bool(x.get("in_stock")), "storage": "gekühlt (Versand in Kühlbox mit Kühlakkus)",
            "shelf_life": None, "shipping_eur": W.SHIPPING_EUR, "nut_flag": "; ".join(flags), "ean": None,
            "portions": int(m.group(1)) if m else None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != W.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.wiesbauer-gourmet.at/wp-json/wc/store/v1/products?category={3138,154,3137}", "fetched": stamp,
           "operator": W.PRODUCER, "vies": {"uid": "ATU20162703", "valid": True, "name": "Wiesbauer Gourmet Gastro GmbH",
           "address": "Wiesbauer Straße 1, AT-3454 Sitzenberg-Reidling", "checked": "2026-10-24T21:13:54Z"},
           "shipping": W.SHIPPING_NOTE, "kept": kept, "excluded": excluded}
    json.dump(out, open(f"raw/wiesbauer_gourmet_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("kept", len(kept), "excluded", len(excluded), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows),
          "with nutrition", sum(1 for r in rows if r["kcal_100"]))


main()
