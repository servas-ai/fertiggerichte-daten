"""SUPPITO webshop (suppito.at; Dr. Andrea Scholdan GmbH, Girardigasse 9, 1060 Wien, FN 571100d, UID ATU77606002 VIES
valid 2026-10-24) → rows 'Online: SUPPITO' in data/online_mealprep.csv (idempotent replace) + evidence
raw/suppito_<stamp>.json (Daten-Squad 2026-10-24T2208).
Source: food-connectors `suppito` adapter (public WooCommerce Store API, robots disallow only wp-admin/add-to-cart),
categories Suppen + Eintöpfe → 18 ready meals (7 soups, 11 stews); excluded sauces (Gemüsesugo, Ragu alla Bolognese),
Brodo, Salatdressing, sweet porridges, spices, drinks, cookbooks.
No nutrition table and no GTIN published → nutrition empty, never estimated. Net weight and €/100 g from the shop's
Germanized fields. veg from the shop's vegan/vegetarisch tags. Photos: first Store API image, vision gate 9/10 PASS
(Butterbeans reuses the Gigantes jar photo → dropped; 8 products publish no photo) — scripts/logo_work_T2208/suppito_photo_sheet.png.
Shipping (suppito.at/lieferbedingungen/): AT chilled Post 10 €/box, min. order 70 €, dispatched Wednesday."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import suppito as S

CSV = "data/online_mealprep.csv"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = S.store_products()
    kept = [S.to_product(sp).to_dict() for sp in shop if S.is_meal(sp)]
    excluded = [{"id": sp["id"], "slug": sp["slug"], "name": sp["name"]} for sp in shop if not S.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; price = d["price_eur"]
        flags = ["keine GTIN/SKU veröffentlicht", "keine Nährwerte veröffentlicht → nicht geschätzt"]
        if not d["image_url"]:
            flags.append("kein Produktfoto veröffentlicht" if x["wc_id"] not in S.BAD_PHOTO else "Shop-Foto zeigt anderes Produkt → verworfen")
        rows.append({"name": d["name"], "brand": "SUPPITO", "store": S.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2) if size else None, "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": S.PRODUCER, "origin": "Hersteller Wien (lt. Impressum); Rohstoffherkunft nicht angegeben",
            "bio": x["bio_claim"], "veg": x["vegetarian"], "prep": "Glas öffnen, erwärmen",
            "category": "Online Meal-Prep",
            "price_source": f"suppito.at WooCommerce Store API Preis/Glas {day} (zzgl. Versand AT 10 €, Mindestbestellwert 70 €)",
            "price_date": day, "packaging": f"Glas {int(size)} g (pfandfrei)" if size else "Glas (pfandfrei)",
            "online": True, "available": bool(x.get("in_stock")), "storage": x["storage"], "shelf_life": x["shelf_life"],
            "shipping_eur": S.SHIPPING_EUR, "nut_flag": "; ".join(flags), "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != S.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.suppito.at/wp-json/wc/store/v1/products?per_page=100", "fetched": stamp,
           "operator": S.PRODUCER, "vies": {"uid": "ATU77606002", "valid": True, "name": "Dr. Andrea Scholdan GmbH",
           "address": "Girardigasse 9, AT-1060 Wien", "checked": "2026-10-24T22:12:01Z"},
           "impressum": "https://www.suppito.at/impressum/ (Dr. Andrea Scholdan GmbH, FN 571100d, HG Wien, ATU77606002)",
           "shipping": S.SHIPPING_NOTE, "storage": f"{S.STORAGE}; {S.SHELF_LIFE}",
           "photo_vision_gate": "9/10 PASS, 51447 rejected (Gigantes photo reused); 8 without photo (scripts/logo_work_T2208/suppito_photo_sheet.png)",
           "kept": kept, "excluded": excluded}
    json.dump(out, open(f"raw/suppito_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("kept", len(kept), "excluded", len(excluded), "online meal-prep",
          sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows),
          "photos", sum(1 for r in rows if r["image_url"]))


main()
