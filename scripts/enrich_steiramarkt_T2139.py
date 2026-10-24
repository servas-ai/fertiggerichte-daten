"""Steira Markt webshop (steiramarkt.at, Seiersberg/Graz; operator Christian Haas, UID ATU67970617 VIES valid
2026-10-24) → rows 'Online: Steira Markt' in data/online_mealprep.csv (idempotent replace) + evidence
raw/steiramarkt_<stamp>.json (Daten-Squad 2026-10-24T2139).
Source: food-connectors `steiramarkt` adapter (public WooCommerce Store API, robots disallow only uploads logs,
add-to-cart and /wp-admin/), categories essen-im-glas-suppen-und-einlagen / kaerntner-kasnudel. Kept 22 ready meals:
8 heat-up jar meals/soups and 14 fresh Kärntner Nudeln; excluded clear broths (PUR), Gulaschsaft, Sugo (pasta sauce),
soup inserts (Fleisch-/Lungenstrudel, Leber-/Kaspressknödel) and a spice gift.
Nutrition only where the shop prints it (Käferbohnensuppe) → others empty, never estimated. No GTIN/SKU published.
Maker hints only from evidence: Mosshammer logo / 'Amlacher Nudel' image in the product gallery, 'SORGER' in the text,
SteirerKraft can on the Käferbohnensuppe photo (vision). Photos: first image per product, vision gate 22/22 PASS
(scripts/logo_work_T2139/steiramarkt_photo_sheet.jpg).
Shipping (page 'Zustellung'): AT chilled Post parcel 19,00 € next day, DPD 10,00 €; DE 20,00 €."""
import sys, json, csv, datetime, re
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import steiramarkt as S

CSV = "data/online_mealprep.csv"
VISION_MAKER = {"1984": "SteirerKraft (Dose auf Produktfoto, vision)"}
VEGAN = re.compile(r"vegan", re.I)
VEG = re.compile(r"Kasnudeln|Spinat|Steinpilz|Knoblauch|Erdäpfel|Tomaten Mozzarella|Kletzen|Heidelbeer|Apfel|Süße", re.I)


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = S.store_products()
    kept = [S.to_product(sp).to_dict() for sp in shop if S.is_meal(sp)]
    excluded = [{"id": sp["id"], "slug": sp["slug"], "name": sp["name"]} for sp in shop if not S.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; price = d["price_eur"]; n = d["nutrition_100g"] or {}
        pp = round(n["protein"] * size / 100, 1) if n.get("protein") and size else None
        nudel = x["line"] == "Kärntner Nudeln"
        flags = ["keine GTIN/SKU veröffentlicht"]
        if not n:
            flags.append("keine Nährwerte veröffentlicht → nicht geschätzt")
        if not size:
            flags.append("Füllmenge nicht angegeben")
        mk = VISION_MAKER.get(str(x["wc_id"])) or x.get("maker_hint")
        m = re.search(r"(\d+)\s*Stück", d["name"])
        rows.append({"name": d["name"], "brand": d["brand"], "store": S.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2) if size else None, "url": d["source_url"], "image_url": d["image_url"],
            "kcal_100": n.get("kcal"), "protein_100": n.get("protein"), "fat_100": n.get("fat"), "satfat_100": n.get("saturated_fat"),
            "carbs_100": n.get("carbs"), "sugar_100": n.get("sugar"), "salt_100": n.get("salt"),
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") and size else None,
            "eur_per_10g_protein": round(price / pp * 10, 2) if pp else None,
            "manufacturer": S.PRODUCER + (f"; Hersteller-Hinweis: {mk}" if mk else ""),
            "origin": "Kärnten (lt. Produkttext)" if nudel and "Kärnten" in x["description"] else "Österreich (Händler Steiermark); Herkunft nicht angegeben",
            "bio": False, "veg": bool(VEGAN.search(d["name"]) or (nudel and VEG.search(d["name"]))) or "Käferbohnen" in d["name"],
            "prep": ("in siedendem Wasser 15–20 min ziehen lassen oder anbraten (lt. Produktseite)" if nudel
                     else "Glas öffnen, im Topf erwärmen"),
            "category": "Online Meal-Prep",
            "price_source": f"steiramarkt.at WooCommerce Store API Preis/Packung {day} (zzgl. Versand AT 10–19 €)",
            "price_date": day, "nut_source": d["source_url"] if n else None,
            "packaging": ("Packung frisch" if nudel else "Glas") + (f" {int(size)} g" if size else ""),
            "online": True, "available": bool(x.get("in_stock")), "storage": x["storage"],
            "shelf_life": None, "shipping_eur": S.SHIPPING_EUR, "nut_flag": "; ".join(flags), "ean": None,
            "portions": None, "_pieces": int(m.group(1)) if m else None})
    for r in rows:
        r.pop("_pieces")
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != S.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.steiramarkt.at/wp-json/wc/store/v1/products?category={491,154}", "fetched": stamp,
           "operator": S.PRODUCER, "vies": {"uid": "ATU67970617", "valid": True, "name": "Haas Christian",
           "address": "Finkengasse 1, AT-8055 Seiersberg-Pirka", "checked": "2026-10-24T21:42:44Z"},
           "impressum": "https://www.steiramarkt.at/impressum/ (Steira Markt, Finkengasse 1, 8055 Seiersberg, ATU67970617)",
           "shipping": S.SHIPPING_NOTE, "photo_vision_gate": "22/22 PASS (scripts/logo_work_T2139/steiramarkt_photo_sheet.jpg)",
           "kept": kept, "excluded": excluded}
    json.dump(out, open(f"raw/steiramarkt_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("kept", len(kept), "excluded", len(excluded), "online meal-prep",
          sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows),
          "with nutrition", sum(1 for r in rows if r["kcal_100"]))


main()
