"""Wagyuhof Frischglas (wagyuhof.com, Wagyuhof GmbH, Haag NÖ) → rows 'Online: Wagyuhof' in data/online_mealprep.csv
(idempotent replace) + company row + logo row + evidence raw/wagyuhof_<stamp>.json (Daten-Squad 2026-10-24T1833).
Source: food-connectors `wagyuhof` adapter (public Shopify storefront JSON + product pages, robots allow).
Kept 4 shelf-stable 300 g jar meals: Wagyu Gulasch, Ragout (Steinpilz-Rahmsoße), Beuschel (13,20 €), Rouladen (14,90 €, sold out).
Nutrition per 100 g (kcal, fat, satfat, carbs, sugar, protein, salt) as published on each product page; Atwater check
within ±3 %; fibre not published → nutriscore left empty. No GTIN (Shopify barcode empty).
Excluded: Wagyu Sugo + Jus (sauces), Rindsuppe (plain broth), '3+1 gratis' multipacks, Frischglas boxes; outside the
collection: Lamm Ragout (raw meat), Pulled Beef (meat component), steaks.
Photos: first image = jar packshot with printed dish label (RINDER GULASCH / RAGOUT / BEUSCHEL / ROULADE, 'Frischglas by
Wagyuhof', 300 g) — vision gate 4/4 PASS (scripts/logo_work_T1833/photo_logo_vision_sheet.jpg).
Shipping AT+DE (Mi/Fr): 14,90 € below 30 €, 9,90 € 30–149,99 €, free from 150 € → shipping_eur 14.90 for one jar."""
import sys, json, csv, datetime, argparse
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import wagyuhof as W

CSV = "data/online_mealprep.csv"; SLUG = "wagyuhof"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stamp"); ap.add_argument("--vies", default="/tmp/wagyu/vies.json"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = W.store_products()
    kept = [W.to_product(sp, W.page(sp["handle"])).to_dict() for sp in shop if W.is_meal(sp)]
    excluded = [{"id": sp["id"], "handle": sp["handle"], "title": sp["title"], "product_type": sp.get("product_type"),
                 "reason": "Sauce/Jus" if any(k in sp["handle"] for k in ("sugo", "jus")) and "3-1" not in sp["handle"] else
                           "Rindsuppe (klare Brühe)" if sp["handle"] == "wagyu-rindsuppe" else
                           "3+1-gratis-Mehrfachpack (Duplikat)" if "3-1-gratis" in sp["handle"] else "Geschenk-/Frischglasbox"}
                for sp in shop if not W.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; n = d["nutrition_100g"]; size = d["size_g"]; price = d["price_eur"]
        at = 9 * n["fat"] + 4 * n["carbs"] + 4 * n["protein"]
        assert abs(at - n["kcal"]) / n["kcal"] < 0.03, (d["name"], at, n["kcal"])
        pp = round(n["protein"] * size / 100, 1)
        rows.append({"name": d["name"], "brand": "Wagyuhof Frischglas", "store": W.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2), "url": d["source_url"], "image_url": d["image_url"],
            "kcal_100": n.get("kcal"), "protein_100": n.get("protein"), "fat_100": n.get("fat"), "satfat_100": n.get("satfat"),
            "carbs_100": n.get("carbs"), "sugar_100": n.get("sugar"), "fiber_100": None, "salt_100": n.get("salt"),
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100), "eur_per_10g_protein": round(price / pp * 10, 2),
            "nutriscore": None, "manufacturer": W.PRODUCER, "origin": "AT (eigene Wagyu-Rinder, Haag NÖ lt. Shop)",
            "bio": False, "veg": False, "prep": "erwärmen (Topf oder Mikrowelle)", "category": "Online Meal-Prep",
            "price_source": f"wagyuhof.com Shopify-Storefront Preis/Glas {day} (zzgl. Versand AT: 14,90 € unter 30 €, 9,90 € ab 30 €, frei ab 150 €)",
            "price_date": day, "nut_source": d["source_url"], "packaging": f"Glas {int(size)} g (Frischglas)",
            "online": True, "available": bool(x.get("available")), "storage": "Frischglas, haltbar ohne Kühlen lt. Shop",
            "shelf_life": None, "shipping_eur": 14.9,
            "nut_flag": "Nährwerte je 100 g lt. Produktseite (Atwater ±3 % ok); Ballaststoffe nicht angegeben → kein Nutri-Score; keine GTIN veröffentlicht",
            "ean": None, "portions": 1})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != W.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    vies = json.load(open(a.vies))
    row = {"slug": SLUG, "name": "Wagyuhof", "role": "producer", "legal_name": "Wagyuhof GmbH",
           "lei": "98450053J99E55F43D03", "register_id": "478220s", "register_authority": "Firmenbuch (LG St. Pölten)", "fn": "478220s",
           "legal_form_code": "GmbH", "country": "AT", "address": "Porstenberg 17, 3350 Haag, AT",
           "entity_status": "eingetragen (Firmenbuch lt. evi.gv.at); LEI ISSUED/ACTIVE; UID aktiv (VIES valid)",
           "parent_direct": None, "parent_ultimate": None, "parent_ultimate_lei": None, "founded": "2017-10-07",
           "owners": "Florian Irxenmayr, Karl Peterseil, Martin Illich-Edlinger (Gesellschafter lt. evi.gv.at)",
           "management": "Florian Irxenmayr (GF seit 2017-10-07); Prokura Karina Freitag (seit 2026-04-20)", "employees": None, "revenue": None,
           "website": "https://wagyuhof.com", "plants": [], "approval_codes": None, "brands": ["Wagyuhof", "Wagyuhof Frischglas", "Frischglas by Wagyuhof"],
           "chains": [W.STORE], "product_count": len(kept), "median_price_eur": sorted(d["price_eur"] for d in kept)[len(kept)//2],
           "median_eur_per_10g_protein": sorted(r["eur_per_10g_protein"] for r in rows)[len(rows)//2],
           "nace": "Zucht, Verarbeitung und Verkauf von Wagyu-Rindfleisch sowie Herstellung von Fleischprodukten (Unternehmensgegenstand lt. Impressum)",
           "sources": ["https://wagyuhof.com/policies/legal-notice", "https://www.evi.gv.at/f/478220s", "https://ec.europa.eu/taxation_customs/vies/",
                       "https://api.gleif.org/api/v1/lei-records?filter[fulltext]=Wagyuhof (1 hit, registeredAs 478220s)"],
           "gleif_match_score": 1.0, "fetched_at": stamp, "chain_product_count": len(kept), "hrb": None, "former_names": None,
           "registry_status": "verified_firmenbuch+vies+gleif (FN 478220s evi.gv.at eingetragen, Stammkapital 35 000 €; UID ATU72584759 VIES 'Wagyuhof GmbH', Porstenberg 17, AT-3350 Haag = Impressum; LEI 98450053J99E55F43D03 registeredAs 478220s)",
           "share_capital": 35000, "register_status": "Eingetragen", "register_entry_date": "2017-10-07", "register_court": "Landesgericht St. Pölten",
           "imprint_url": "https://wagyuhof.com/policies/legal-notice", "uid": "ATU72584759", "uid_vies_name": vies.get("name"),
           "uid_vies_address": (vies.get("address") or "").replace("\n", ", "), "uid_checked_at": vies.get("requestDate")}
    P = "data/companies.json"; dd = [r for r in json.load(open(P)) if r["slug"] != SLUG]; dd.append(row)
    json.dump(dd, open(P, "w"), ensure_ascii=False, indent=1)
    C = "data/companies.csv"; cc = list(csv.DictReader(open(C, encoding="utf-8"))); ccols = list(cc[0].keys())
    cc = [r for r in cc if r["slug"] != SLUG]
    o = {c: row.get(c) for c in ccols}; o["brands"] = "|".join(row["brands"]); o["chains"] = "|".join(row["chains"])
    if "plants_count" in o: o["plants_count"] = 0
    with open(C, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(cc)
        w.writerow({k: ("" if v is None else (json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v)) for k, v in o.items()})
    LR = {"slug": SLUG, "name": "Wagyuhof", "category": "Markenhersteller", "file": "logos/wagyuhof.png",
          "source_url": "https://wagyuhof.com/cdn/shop/files/Wagyu_das_beste_Fleisch_der_Welt.svg (Shopify header logo SVG, robots allow; rendered to PNG 800x344 with cairosvg, transparent background, otherwise unmodified; vision gate PASS; files staged in fertiggerichte-daten scripts/logo_work_T1833 for the Orchestrator merge)",
          "brands": ["Wagyuhof", "Wagyuhof Frischglas", W.STORE, "Wagyuhof GmbH"]}
    LJ = "data/logos.json"; lj = [r for r in json.load(open(LJ)) if r["slug"] != SLUG]; lj.append(LR)
    json.dump(lj, open(LJ, "w"), ensure_ascii=False, indent=1)
    LC = "data/logos.csv"; lc = list(csv.DictReader(open(LC, encoding="utf-8"))); lcols = list(lc[0].keys())
    lc = [r for r in lc if r["slug"] != SLUG]
    with open(LC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lc); w.writerow({k: ("|".join(LR["brands"]) if k == "brands" else LR.get(k, "")) for k in lcols})
    out = {"source": "wagyuhof.com public Shopify storefront (food-connectors wagyuhof adapter)", "fetched": stamp,
           "robots": "User-agent * disallows only cart/checkout/orders/account, sort/filter collection URLs, recommendations",
           "operator": {"name": "Wagyuhof GmbH", "address": "Porstenberg 17, 3350 Haag", "fn": "478220s", "court": "LG St. Pölten",
                        "uid": "ATU72584759", "lei": "98450053J99E55F43D03", "md": "Florian Irxenmayr", "source": "https://wagyuhof.com/policies/legal-notice"},
           "shipping": {"source": "https://wagyuhof.com/policies/shipping-policy", "countries": ["AT", "DE"], "days": "Mittwoch und Freitag",
                        "fees": [{"from": 0, "to": 29.99, "eur": 14.9}, {"from": 30, "to": 149.99, "eur": 9.9}, {"from": 150, "eur": 0}],
                        "delivers_linz": True, "delivers_linz_basis": "Lieferung 'nach ganz Österreich' lt. Versandseite"},
           "vision_gate": {"photos": "4/4 PASS (jar packshots, printed label names the dish, 300 g)", "logo": "PASS (official header logo: bull + WAGYUHOF wordmark)"},
           "kept": len(kept), "with_nutrition": sum(bool(d["nutrition_100g"]) for d in kept), "with_gtin": 0,
           "excluded": excluded, "products": kept, "logo": LR,
           "company_evidence": {"vies": vies, "evi": "https://www.evi.gv.at/f/478220s (Status Eingetragen, Eintragungsdatum 07.10.2017, Stammkapital EUR 35 000)",
                                "gleif": {"lei": "98450053J99E55F43D03", "status": "ISSUED", "entity_status": "ACTIVE", "registeredAs": "478220s"}}}
    json.dump(out, open(f"raw/wagyuhof_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("kept", len(kept), "with nutrition", out["with_nutrition"], "excluded", len(excluded), "csv rows", len(cur) + len(rows), "companies", len(dd), "logos", len(lj))

if __name__ == "__main__":
    main()
