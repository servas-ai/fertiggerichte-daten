"""voeslauermanufaktur webshop (voeslauermanufaktur.at; Inh. Isabella Schnabel, Einzelunternehmen/Kleinunternehmen,
Flugfeldstraße 4, 2540 Bad Vöslau NÖ; WKNÖ member, Gewerbebehörde BH Baden; no Firmenbuch entry and no UID
published → VIES not applicable) → rows 'Online: voeslauermanufaktur' in data/online_mealprep.csv (idempotent replace)
+ evidence raw/voeslauermanufaktur_<stamp>.json (Daten-Squad 2026-10-24T2236).
Source: food-connectors `voeslauermanufaktur` adapter (server-rendered Jimdo pages Hauptgerichte + Suppen, schema.org
microdata; robots Crawl-Delay 5 honoured; /j/ disallowed → never fetched) → 13 heat-up jar meals (6 mains, 7 soups);
excluded the clear broth 'Echtes Rindssupperl'; sides (Letscho, Sauerkraut, gegrillte Tomaten), Sugo, Pesto,
Antipasti not taken.
No nutrition table and no GTIN published → nutrition empty, never estimated. veg only from the shop's 'vegan' badge.
Photos: Jimdo main image, vision gate 11/12 PASS ('Erdäpfelcremesuppe mit Speck' shows the byte-identical photo of
the plain Erdäpfelcremesuppe → dropped; Rindssupperl mit Fleischeinlage has no photo) —
scripts/logo_work_T2236/voeslauermanufaktur_photo_sheet.png.
Shipping (AGB §4.6/§6): delivery to the order address in Austria (7 working days; shop badge 3–5 days), free within
Austria from 180 €; fee below 180 € shown only in the checkout → shipping_eur empty."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import voeslauermanufaktur as V

CSV = "data/online_mealprep.csv"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = V.store_products()
    kept = [V.to_product(sp).to_dict() for sp in shop if V.is_meal(sp)]
    excluded = [{"id": sp["id"], "name": sp["name"], "reason": "klare Suppe (Brühe)"} for sp in shop if not V.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; price = d["price_eur"]
        flags = ["keine GTIN/SKU veröffentlicht", "keine Nährwerte veröffentlicht → nicht geschätzt"]
        if not d["image_url"]:
            flags.append("Shop-Foto zeigt anderes Produkt → verworfen" if x["jimdo_id"] in V.BAD_PHOTO else "kein Produktfoto veröffentlicht")
        rows.append({"name": d["name"], "brand": "voeslauermanufaktur", "store": V.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2) if size else None, "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": V.PRODUCER, "origin": "Hersteller Bad Vöslau NÖ (lt. Impressum/AGB); Rohstoffherkunft nur wo im Zutatentext genannt",
            "bio": x["bio_claim"], "veg": x["vegetarian"], "prep": "Glas öffnen, erwärmen",
            "category": "Online Meal-Prep",
            "price_source": f"voeslauermanufaktur.at Jimdo-Shop Preis/Glas {day} (zzgl. Versand; AT versandkostenfrei ab 180 €)",
            "price_date": day, "packaging": f"Glas {int(size)} g" if size else "Glas",
            "online": True, "available": bool(x.get("in_stock")), "storage": x["storage"], "shelf_life": None,
            "shipping_eur": V.SHIPPING_EUR, "nut_flag": "; ".join(flags), "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != V.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": [V.BASE + p for p in V.PAGES.values()], "fetched": stamp,
           "operator": V.PRODUCER,
           "vies": {"uid": None, "valid": None, "note": "Einzelunternehmen/Kleinunternehmen: keine UID und kein FN im Impressum/AGB veröffentlicht → VIES nicht anwendbar"},
           "impressum": "https://www.voeslauermanufaktur.at/rechtliches/impressum/ (Inhaberin Isabella Schnabel, Einzelunternehmen, Flugfeldstraße 4, 2540 Bad Vöslau, WKNÖ, BH Baden)",
           "shipping": V.SHIPPING_NOTE, "storage": V.STORAGE,
           "photo_vision_gate": "11/12 PASS, mbd085715cb6d6dd5 rejected (byte-identical Erdäpfelcremesuppe photo); 1 without photo (scripts/logo_work_T2236/voeslauermanufaktur_photo_sheet.png)",
           "kept": kept, "excluded": excluded}
    json.dump(out, open(f"raw/voeslauermanufaktur_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("kept", len(kept), "excluded", len(excluded), "online meal-prep",
          sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows),
          "photos", sum(1 for r in rows if r["image_url"]))


main()
