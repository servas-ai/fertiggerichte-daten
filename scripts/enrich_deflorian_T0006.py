"""Deflorian webshop (deflorian.tirol; Deflorian Tiefkühlspezialitäten GmbH, Hnr. 35b, 6069 Gnadenwald, Tirol;
UID ATU64259769 VIES valid 2026-10-25 'Deflorian Tiefkühlspezialitäten GmbH', LG Innsbruck) → rows 'Online: Deflorian'
in data/online_mealprep.csv (idempotent replace) + evidence raw/deflorian_<stamp>.json; existing company row
deflorian-srl gets the new chain; logo 'deflorian' already present (Daten-Squad 2026-10-25T0006).
Source: food-connectors `deflorian` adapter (public Shopify products.json, robots Allow: /, + product pages for the
'ZUTATEN' accordion at 1 req/s) → 27 frozen ready meals. Price = smallest pack incl. MwSt.; size = Shopify variant
weight. No nutrition/GTIN published on the shop → left empty, never estimated (MPreis carries the same products with EAN).
Photos: first product image, vision gate 27/27 PASS (contact sheet reviewed 2026-10-25).
Shipping: AT-wide only, frozen with dry ice on Thursdays, 14,99 € below 40 €, free from 40 €."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import deflorian as D

CSV = "data/online_mealprep.csv"
VEG_NO = ("fleisch", "speck", "hühner", "huhn", "rind", "schwein", "selch")


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = D.store_products()
    kept = [p.to_dict() for p in D.Deflorian().fetch()]
    excluded = [{"id": sp["id"], "name": sp["title"], "tags": sp.get("tags"), "reason": "Sauce/Beilage/Suppeneinlage/Gebäck/Paket/Gutschein, kein Fertiggericht"}
                for sp in shop if not D.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; price = d["price_eur"]; ing = (x.get("ingredients") or "").lower()
        rows.append({"name": d["name"], "brand": "Deflorian", "store": D.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2) if size else None, "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": D.PRODUCER, "origin": d["origin"], "bio": False,
            "veg": (not any(w in ing for w in VEG_NO)) if ing else None,
            "prep": "tiefgekühlt; kochen/erwärmen lt. Packung", "category": "Online Meal-Prep",
            "price_source": f"deflorian.tirol Shopify-Storefront Preis kleinste Packung ({x.get('pack')}) {day} (Versand AT 14,99 € unter 40 €, ab 40 € frei; nur Österreich, donnerstags)",
            "price_date": day, "packaging": f"{x.get('pack')} ({int(size)} g)" if size else x.get("pack"),
            "online": True, "available": bool(x.get("available")), "storage": x["storage"], "shelf_life": "",
            "shipping_eur": D.SHIPPING_EUR,
            "nut_flag": "keine Nährwerte/GTIN im Shop veröffentlicht → nicht geschätzt; Zutaten/Allergene von der Produktseite; Gewicht = Shopify-Variantengewicht",
            "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != D.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": D.BASE + "/products.json?limit=250 + /products/<handle> (ZUTATEN)", "fetched": stamp, "operator": D.PRODUCER,
           "vies": {"uid": "ATU64259769", "valid": True, "name": "Deflorian Tiefkühlspezialitäten GmbH", "address": "Hnr 35b, AT-6069 Gnadenwald", "checked": "2026-10-25T00:09:51Z"},
           "impressum": "https://deflorian.tirol/policies/legal-notice (Deflorian Tiefkühlspezialitäten GmbH, Hnr. 35b, 6069 Gnadenwald; UID ATU64259769; Firmenbuchgericht LG Innsbruck; 'Firmenbuchnummer AT70258EG' as printed — looks like an approval number, not an FN, so not used)",
           "shipping": D.SHIPPING_NOTE, "photo_vision_gate": "27/27 PASS (contact sheet of first product images)",
           "kept": kept, "excluded": excluded}
    json.dump(out, open(f"raw/deflorian_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    for r in comp:
        if r["slug"] == "deflorian-srl" and D.STORE not in r["chains"]:
            r["chains"] = "|".join([c for c in r["chains"].split("|") if c] + [D.STORE])
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "excluded", len(excluded), "online meal-prep",
          sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
