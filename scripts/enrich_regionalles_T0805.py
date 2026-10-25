"""RegionAlles Joglland webshop (regionalles.com; RegionALLES WB OG, Arzberg 51, 8253 Waldbach-Mönichwald, Stmk; FN 537480m per
Impressum; UID ATU75793759 VIES valid 2026-10-25 same name/address; GLEIF no LEI) — 6 jar ready meals from regional producers
(Gastwirtschaft Hold, Biohof Krautgartner, Jobi Forellengasthof). Source: food-connectors `regionalles` (Shopify products.json).
No nutrition/GTIN published → empty. Photos vision-checked 5/6 (Chili sin Carne reuses the con-Carne packshot → no photo).
Shipping per FAQ: Post AG Austria-wide, chilled at extra cost, free from 79 € (cost below 79 € not published → shipping_eur empty).
Usage: python3 scripts/enrich_regionalles_T0805.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import regionalles as M

CSV = "data/online_mealprep.csv"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in M.all_products()]
    rows = []
    for d in kept:
        x = d["extra"]
        flags = ["keine Nährwerte und keine GTIN auf regionalles.com → nicht geschätzt", f"Produzent lt. Produktseite: {d['producer']}"]
        flags.append("Füllmenge 0,427 l lt. Produktseite (Volumen, als g übernommen)" if d["size_g"] == 427.0 else "Nettofüllmenge 430 ml lt. Etikett (Packshot)")
        if not d["image_url"]:
            flags.append("Packshot zeigt Chili con Carne-Etikett → Foto verworfen (Vision-Gate)")
        if not x["in_stock"]:
            flags.append("derzeit nicht verfügbar (Shopify available=false)")
        rows.append({"name": d["name"], "brand": d["brand"], "store": M.STORE, "price_eur": d["price_eur"], "size_g": d["size_g"] or "",
             "price_per_kg": d["unit_price_eur"] or "", "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": d["producer"], "producer_id": "", "origin": "AT (Steiermark, Joglland)",
             "bio": x["bio"], "veg": x["veg"], "prep": "im Glas haltbar gemacht – nur erwärmen", "category": "Online Meal-Prep",
             "price_source": f"regionalles.com Shopify products.json {day}, inkl. USt. und Pfandglas; {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "", "packaging": "Pfandglas", "online": True, "available": x["in_stock"],
             "storage": "ungekühlt haltbar (eingekocht)", "shelf_life": "", "shipping_eur": "", "nut_flag": "; ".join(flags), "ean": "", "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://www.regionalles.com/products.json?limit=250 (Shopify, 1 request)", "fetched": stamp,
           "robots": "Shopify default: Allow / incl. products; no disallow for /products.json",
           "operator": "RegionALLES WB OG", "fn": "FN 537480m",
           "impressum": {"https://www.regionalles.com/pages/impressum": "RegionALLES WB OG, Arzberg 51, 8253 Waldbach; Tel. +43 676 9276528; info@regionalles.com; FN 537480m; UID ATU 75793759"},
           "vies": {"uid": "ATU75793759", "valid": True, "checked": "2026-10-25T08:09:00Z", "name": "RegionALLES WB OG", "address": "Arzberg 51/1, AT-8253 Waldbach-Mönichwald"},
           "gleif": "fulltext 'RegionALLES' 0 hits → no LEI",
           "shipping": {"https://www.regionalles.com/pages/faq": "RegionAlles liefert österreichweit mit unserem Partner der Post AG aus ... Kühlversand möglich (zusätzliche Versandkosten); kein Mindestbestellwert; header 'Versandkostenfrei ab 79 EUR!'"},
           "photo_vision_gate": "5/6 PASS (Hold Gulasch/Chili con Carne/Leberknödelsuppe jars, Krautgartner Putengulasch jar, Feistritztaler Fisch-Suppe 430 ml); FAIL Chili sin Carne (label reads 'Chili con carne')",
           "excluded": ["Ehrenhöfer's Leberkäs im Glas ×3 (cold meat loaf)", "Jobi Roller / Der Schorfe (pickled fish)", "sauces, mustard, rice noodles"],
           "kept": kept}
    json.dump(out, open(f"raw/regionalles_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "regionalles"]
    ap = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "regionalles", "name": "RegionAlles Joglland", "role": "retailer",
        "legal_name": "RegionALLES WB OG", "fn": "FN 537480m", "register_id": "FN 537480m", "register_authority": "Firmenbuch",
        "legal_form_code": "OG", "country": "AT", "address": "Arzberg 51/1, AT-8253 Waldbach-Mönichwald", "entity_status": "UID VIES gültig; kein LEI",
        "website": "https://www.regionalles.com", "product_count": len(rows), "median_price_eur": ap[len(ap) // 2], "fetched_at": stamp,
        "brands": "Gastwirtschaft Hold|Biohof Krautgartner|Jobi", "chains": M.STORE, "uid": "ATU75793759", "uid_vies_name": "RegionALLES WB OG",
        "uid_vies_address": "Arzberg 51/1, AT-8253 Waldbach-Mönichwald", "uid_checked_at": "2026-10-25T08:09Z",
        "imprint_url": "https://www.regionalles.com/pages/impressum", "registry_status": "fn_from_impressum_uid_vies_valid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
