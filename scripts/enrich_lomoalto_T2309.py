"""Lomo Alto webshop (lomoalto.at; LOMO ALTO OG, Atzgersdorf 4, 4141 Pfarrkirchen im Mühlkreis OÖ; UID ATU77712619
VIES valid 2026-10-24 'Lomo Alto OG'; no FN published, no GLEIF record) → rows 'Online: Lomo Alto' in
data/online_mealprep.csv (idempotent replace) + company row + logo row + evidence raw/lomoalto_<stamp>.json
(Daten-Squad 2026-10-24T2309).
Source: food-connectors `lomoalto` adapter (public Shopify products.json, robots Allow: /) → 3 Bio heat-up jar meals
400 g (Rindergulasch, Rotweinragout, Chili con Carne); Knochensuppe (broth), Sulz, Nierenfett, Leberpasteten excluded.
Ingredients, nutrition per 100 g and EAN-13 transcribed by hand from the shop's own label images (copies in
scripts/logo_work_T2309/lomoalto_etikett_*.jpg; EAN check digits valid); label gives kJ only → kcal = kJ/4.184
(Atwater-consistent: Gulasch 147.8 vs 147.6, Chili 84.6+fibre vs 86.6, Ragout incl. 9 % Rotwein). Fibre not printed
→ nutriscore empty. Photos: first product image (jar packshot), vision gate 3/3 PASS
(scripts/logo_work_T2309/lomoalto_photo_sheet.png). Shipping: AT only, fee only in checkout → shipping_eur empty."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import lomoalto as L

CSV = "data/online_mealprep.csv"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = L.store_products()
    kept = [L.to_product(sp).to_dict() for sp in shop if L.is_meal(sp)]
    excluded = [{"id": sp["id"], "name": sp["title"], "sku": L._sku(sp), "reason": "Brühe/Sulz/Fett/Pastete, kein Fertiggericht"}
                for sp in shop if L._sku(sp).startswith("FERTIGP") and not L.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; price = d["price_eur"]; n = d["nutrition_100g"]
        pp = round(n["protein"] * size / 100, 1) if n.get("protein") else None
        flags = ["Nährwerte je 100 g, Zutaten und EAN vom Shop-Etikettbild transkribiert; kcal = kJ/4,184",
                 "Ballaststoffe nicht angegeben → kein Nutri-Score"] if n else ["keine Nährwerte"]
        rows.append({"name": d["name"], "brand": "LOMO ALTO", "store": L.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2), "url": d["source_url"], "image_url": d["image_url"],
            "kcal_100": n.get("kcal"), "protein_100": n.get("protein"), "fat_100": n.get("fat"), "satfat_100": n.get("satfat"),
            "carbs_100": n.get("carbs"), "sugar_100": n.get("sugar"), "fiber_100": None, "salt_100": n.get("salt"),
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") else None,
            "eur_per_10g_protein": round(price / pp * 10, 2) if pp else None, "nutriscore": None,
            "manufacturer": L.PRODUCER, "origin": "AT (Mühlviertler Bio-Rind, eigener Betrieb Pfarrkirchen OÖ lt. Shop/Etikett)",
            "bio": True, "veg": False, "prep": "Glas öffnen, erwärmen", "category": "Online Meal-Prep",
            "price_source": f"lomoalto.at Shopify-Storefront Preis/Glas {day} (zzgl. Versand, Kosten erst im Bestellvorgang; Lieferung nur AT)",
            "price_date": day, "nut_source": x.get("label_image") or "", "packaging": f"Glas {int(size)} g",
            "online": True, "available": bool(x.get("available")), "storage": x["storage"], "shelf_life": x["shelf_life"],
            "shipping_eur": L.SHIPPING_EUR, "nut_flag": "; ".join(flags), "ean": d["ean"], "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != L.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": L.BASE + "/products.json?limit=250", "fetched": stamp, "operator": L.PRODUCER,
           "vies": {"uid": "ATU77712619", "valid": True, "name": "Lomo Alto OG", "address": "Atzgersdorf 4, AT-4141 Pfarrkirchen/Mühlkreis", "checked": "2026-10-24T23:10:24Z"},
           "gleif": "no record for 'Lomo Alto OG' (api.gleif.org 2026-10-24)",
           "impressum": "https://lomoalto.at/policies/legal-notice (LOMO ALTO OG, Atzgersdorf 4, 4141 Pfarrkirchen; UID ATU77712619; Inhaber Martin Sageder & Josef Wiesinger; Gerichtsstand Rohrbach; kein FN genannt)",
           "shipping": L.SHIPPING_NOTE, "labels": {k: v for k, v in L.LABEL.items()},
           "photo_vision_gate": "3/3 PASS (scripts/logo_work_T2309/lomoalto_photo_sheet.png)",
           "kept": kept, "excluded": excluded}
    json.dump(out, open(f"raw/lomoalto_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    # company row (idempotent)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "lomo-alto"]
    comp.append({c: "" for c in ccols} | {"slug": "lomo-alto", "name": "Lomo Alto", "role": "producer", "legal_name": "LOMO ALTO OG",
        "legal_form_code": "OG", "country": "AT", "address": "Atzgersdorf 4, 4141 Pfarrkirchen im Mühlkreis, AT",
        "entity_status": "UID aktiv (VIES valid); kein FN im Impressum, kein LEI", "owners": "Martin Sageder, Josef Wiesinger (Geschäftsinhaber lt. Impressum)",
        "website": "https://lomoalto.at", "product_count": len(rows),
        "median_price_eur": sorted(r["price_eur"] for r in rows)[len(rows)//2],
        "median_eur_per_10g_protein": sorted(r["eur_per_10g_protein"] for r in rows)[len(rows)//2],
        "fetched_at": stamp, "brands": "LOMO ALTO|Lomo Alto Organico|Mühlviertler Bio-Rind", "chains": L.STORE, "plants_count": "0",
        "uid": "ATU77712619", "uid_vies_name": "Lomo Alto OG", "uid_vies_address": "Atzgersdorf 4, AT-4141 Pfarrkirchen/Mühlkreis",
        "uid_checked_at": "2026-10-24T23:10:24.032Z", "imprint_url": "https://lomoalto.at/policies/legal-notice",
        "register_court": "", "registry_status": "verified_vies (UID ATU77712619 VIES 'Lomo Alto OG', Atzgersdorf 4, AT-4141 Pfarrkirchen/Mühlkreis = Impressum; FN not published, not looked up; no GLEIF record; label producer 'Stressfrei Biofleisch GesbR' same address)"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    lp = "data/logos.csv"; lg = list(csv.DictReader(open(lp, encoding="utf-8"))); lcols = list(lg[0].keys())
    lg = [r for r in lg if r["slug"] != "lomo-alto"]
    lg.append({"slug": "lomo-alto", "name": "Lomo Alto", "category": "Markenhersteller", "file": "logos/lomo-alto.png",
        "source_url": "https://lomoalto.at/cdn/shop/files/logo.png (Shopify header logo, robots allow; original 178x95 palette PNG, white on transparent, unmodified; vision gate PASS on grey; staged in fertiggerichte-daten scripts/logo_work_T2309 for the Orchestrator merge)",
        "brands": "LOMO ALTO|Lomo Alto Organico|Online: Lomo Alto|LOMO ALTO OG"})
    with open(lp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lg)
    print("kept", len(kept), "excluded", len(excluded), "online meal-prep",
          sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows), "companies", len(comp), "logos", len(lg))


main()
