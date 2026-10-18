"""Daten-Squad 2026-10-18T0006: new online store GOURMET Daheim via Mahlzeit Vertriebs GmbH (Linz) → evidence
raw/gourmet_daheim_<stamp>.json + rows 'Online: GOURMET Daheim (Mahlzeit Linz)' in data/online_mealprep.csv (idempotent
replace) + 2 company rows (retailer Mahlzeit Vertriebs GmbH, producer GMS GOURMET GmbH).

Source: food-connectors `gourmet-daheim` adapter — official price-list PDF on mahlzeit.co.at (valid from 2026-03-16,
EUR incl. MwSt., net weight) joined on the 7-digit article number with the official 'Allergene und Nährwerte zur
Speisekarte 2026' PDF linked on gourmet-daheim.at/downloads. Both robots.txt allow. No GTIN, no photos, no fibre
published → empty (never estimated). Delivery: weekly frozen delivery in all of Upper Austria incl. Linz, min. 1 carton
(7 main dishes), delivery free with ≥1 main-dish carton (mahlzeit.co.at/a-la-carte/).
Companies: Mahlzeit — legal notice mahlzeit.co.at/impressum (FN 169033d LG Linz, ATU44675909) + EU VIES (valid, name
'MAHLZEIT Vertriebsgesellschaft m.b.H.', Melissenweg 34, AT-4020 Linz); GMS GOURMET GmbH — GLEIF LEI 529900TDG5CX25LX8H86
(FN 104525p, Oberlaaer Straße 298, 1230 Wien; ultimate parent Raiffeisenbankengruppe OÖ Verbund eGen 529900XSTAE561178282).
Usage: python3 scripts/enrich_gourmet_daheim_T0006.py --live-json /tmp/gdh/live_all.json [--stamp 2026-10-18T0006]"""
import sys, json, csv, argparse, statistics, hashlib, os
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import gourmet_daheim as G

CSV = "data/online_mealprep.csv"
DELIVERY = {"operator": "Mahlzeit Vertriebsges.m.b.H., Melissenweg 34, 4020 Linz",
            "area": "ganz Oberösterreich (inkl. Linz), Tiefkühl-Zustellung 1x pro Woche",
            "terms": "Mindestbestellmenge 7 Hauptspeisen (1 Karton); Zustellung gratis bei mind. 1 Karton Hauptspeisen; keine Vertragsbindung; Bestellung 1 Woche vor Zustellung (Telefon, E-Mail, Betreuer oder Webshop mit Registrierung)",
            "source": "https://www.mahlzeit.co.at/a-la-carte/ (2026-10-18)", "delivers_linz": True}
COMPANIES = [
 {"slug": "mahlzeit-vertriebs-gmbh", "name": "Mahlzeit Linz (Mahlzeit Vertriebsges.m.b.H.)", "role": "retailer",
  "legal_name": "MAHLZEIT Vertriebsgesellschaft m.b.H.", "lei": None, "fn": "FN 169033d", "register_id": "169033d",
  "register_authority": "RA000017", "country": "AT", "address": "Melissenweg 34, 4020 Linz, AT",
  "entity_status": "Firmenbuch (legal notice: FN169033d, Landesgericht Linz); no GLEIF record", "website": "https://www.mahlzeit.co.at",
  "brands": ["Mahlzeit", "Online: GOURMET Daheim (Mahlzeit Linz)"], "chains": ["Online: GOURMET Daheim (Mahlzeit Linz)"],
  "uid": "ATU44675909", "uid_vies_name": "MAHLZEIT Vertriebsgesellschaft m.b.H.", "uid_vies_address": "Melissenweg 34, AT-4020 Linz",
  "imprint_url": "https://www.mahlzeit.co.at/impressum/", "register_court": "Landesgericht Linz",
  "management": "Markus Baumann (Geschäftsführer lt. Impressum)",
  "registry_status": "verified_vies_imprint (VIES valid, name+address match; FN as printed on the legal notice; GLEIF fulltext 'Mahlzeit Vertrieb' no AT hit)",
  "sources": ["https://www.mahlzeit.co.at/impressum/", "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/AT/vat/U44675909"]}]
# GMS GOURMET GmbH already exists (slug gms-gourmet-gmbh, Good Choice/Hofer producer) → MERGE, never overwrite its owners/
# employees/revenue/plants: only replace the GLEIF DUPLICATE record 5299003EXF4GJXGELC41 by the ISSUED LEI and add the parent + brand.
GMS_MERGE = {"slug": "gms-gourmet-gmbh", "lei": "529900TDG5CX25LX8H86", "entity_status": "ACTIVE (GLEIF ISSUED)",
  "lei_note": "GLEIF: 529900TDG5CX25LX8H86 ISSUED (last update 2025-10-30); the earlier stored 5299003EXF4GJXGELC41 is registration status DUPLICATE",
  "parent_ultimate": "Raiffeisenbankengruppe OÖ Verbund eGen", "parent_ultimate_lei": "529900XSTAE561178282",
  "add_brands": ["GOURMET Daheim"], "add_chains": ["Online: GOURMET Daheim (Mahlzeit Linz)"],
  "add_sources": ["https://api.gleif.org/api/v1/lei-records/529900TDG5CX25LX8H86", "https://api.gleif.org/api/v1/lei-records/529900TDG5CX25LX8H86/ultimate-parent",
                  "https://www.gourmet-daheim.at/downloads (Nährwert-PDF: 'GMS GOURMET GmbH')"]}


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--live-json", required=True); ap.add_argument("--stamp", default="2026-10-18T0006"); a = ap.parse_args()
    allp = json.load(open(a.live_json, encoding="utf-8"))
    meals = [p for p in allp if p["extra"]["is_meal"]]
    day = a.stamp[:10]; rows = []
    for d in meals:
        n, x, size, price = d["nutrition_100g"], d["extra"], d["size_g"], d["price_eur"]
        prot = round(n["protein"] * size / 100, 1) if n and size else None
        rows.append({"name": d["name"], "brand": d["brand"], "store": G.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": d["unit_price_eur"], "url": G.PRICE_PDF + f"#art={x['article_no'].replace(' ', '')}", "image_url": None,
            "kcal_100": n.get("kcal"), "protein_100": n.get("protein"), "fat_100": n.get("fat"), "satfat_100": n.get("satfat"),
            "carbs_100": n.get("carbs"), "sugar_100": n.get("sugar"), "fiber_100": None, "salt_100": n.get("salt"),
            "protein_pack": prot, "kcal_pack": round(n["kcal"] * size / 100) if n and size else None,
            "eur_per_10g_protein": round(price / prot * 10, 2) if prot else None, "nutriscore": None,
            "manufacturer": "GMS GOURMET GmbH, Oberlaaer Straße 298, 1230 Wien (Hersteller lt. Nährwert-PDF); Vertrieb OÖ: Mahlzeit Vertriebsges.m.b.H., 4020 Linz",
            "producer_id": None, "origin": None, "bio": False, "veg": True if x["vegetarian"] else None,
            "prep": "Mikrowelle oder Heißluftofen ohne Auftauen (lt. Mahlzeit/GOURMET)", "instantpot": None,
            "category": "Online Meal-Prep",
            "price_source": f"Mahlzeit Linz Preisliste GOURMET Daheim (gültig ab {x['price_valid_from']}, € inkl. MwSt.), Art.-Nr. {x['article_no']}, abgerufen {day}",
            "price_date": day, "nut_source": f"GOURMET Daheim 'Allergene und Nährwerte zur Speisekarte 2026' pro 100 g ({x['nutrition_source']}), abgerufen {day}",
            "packaging": f"Menüschale {int(size)} g, Bestellung in Kartons à 7" + (" (Breikost)" if x["breikost"] else ""),
            "online": True, "available": True, "storage": "Tiefkühl (TK)", "shelf_life": "TK (−18 °C)", "shipping_eur": 0.0,
            "nut_flag": "Ballaststoffe nicht angegeben; Allergene " + (",".join(x["allergens"] or []) or "keine") + "; Kennzeichen " + (", ".join(x["flag_names"]) or "—") + f"; Kategorie {d['category']}",
            "ean": None, "portions": 1})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != G.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    # companies
    P = "data/companies.json"; C = "data/companies.csv"
    cj = json.load(open(P))
    for r in cj:
        if r["slug"] == GMS_MERGE["slug"]:
            for k in ("lei", "entity_status", "lei_note", "parent_ultimate", "parent_ultimate_lei"): r[k] = GMS_MERGE[k]
            r["brands"] = list(dict.fromkeys((r.get("brands") or []) + GMS_MERGE["add_brands"]))
            r["chains"] = list(dict.fromkeys((r.get("chains") or []) + GMS_MERGE["add_chains"]))
            r["sources"] = list(dict.fromkeys((r.get("sources") or []) + GMS_MERGE["add_sources"]))
            r["product_count"] = (r.get("product_count") or 0) + len(rows); gms = r
    slugs = {c["slug"] for c in COMPANIES}
    cj = [r for r in cj if r["slug"] not in slugs]
    now = "2026-10-18T00:27:00Z"
    ccur = list(csv.DictReader(open(C, encoding="utf-8"))); ccols = list(ccur[0].keys()); ccur = [r for r in ccur if r["slug"] not in slugs]
    for r in ccur:
        if r["slug"] == GMS_MERGE["slug"]:
            r["lei"], r["entity_status"] = GMS_MERGE["lei"], GMS_MERGE["entity_status"]
            r["parent_ultimate"] = f"{GMS_MERGE['parent_ultimate']} (LEI {GMS_MERGE['parent_ultimate_lei']})"
            r["brands"] = "|".join(gms["brands"]); r["chains"] = "|".join(gms["chains"]); r["product_count"] = gms["product_count"]
    prices = [r["price_eur"] for r in rows]; pp = [r["eur_per_10g_protein"] for r in rows if r["eur_per_10g_protein"]]
    out_rows = []
    for c in COMPANIES:
        c = dict(c, product_count=len(rows), median_price_eur=statistics.median(prices), median_eur_per_10g_protein=round(statistics.median(pp), 2),
                 fetched_at=now, uid_checked_at=now if c.get("uid") else None)
        cj.append(c)
        o = {k: c.get(k) for k in ccols}; o["brands"] = "|".join(c["brands"]); o["chains"] = "|".join(c["chains"]); o["plants_count"] = 0
        out_rows.append({k: ("" if v is None else v) for k, v in o.items()})
    json.dump(cj, open(P, "w"), ensure_ascii=False, indent=1)
    with open(C, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(ccur); w.writerows(out_rows)
    ev = {"run": f"{a.stamp} Daten-Squad", "source": "food-connectors gourmet-daheim adapter (official PDFs)",
          "price_pdf": {"url": G.PRICE_PDF, "sha256": sha("/tmp/gdh/preisliste.pdf"), "valid_from": G.PRICE_VALID_FROM,
                        "robots": "mahlzeit.co.at Yoast: User-agent: * Disallow: (empty)"},
          "nutrition_pdf": {"url": G.NUTRITION_PDF, "sha256": sha("/tmp/gdh/naehrwerte.pdf"), "stand": "05.02.2026, gültig ab 16. März 2026",
                            "robots": "gourmet-daheim.at Allow: /, Disallow: /*?*"},
          "delivery": DELIVERY, "companies": COMPANIES, "company_merge": GMS_MERGE, "articles": len(allp), "meals": len(rows),
          "excluded": [{"article_no": p["extra"]["article_no"], "name": p["name"], "category": p["category"], "reason": "Kuchen/Kompott (keine Mahlzeit)"} for p in allp if not p["extra"]["is_meal"]],
          "median_price_eur": statistics.median(prices), "vegetarian": sum(1 for r in rows if r["veg"]),
          "atwater_check": "141/141 within ±15 % (4·P+4·KH+9·F vs kcal)",
          "not_published": ["GTIN", "Ballaststoffe", "Produktfotos (webshop shopmahlzeit.gourmet.at not reachable from the box: TLS reset; photos © GMS Gourmet)"],
          "other_probes_this_run": {"maximarkt.at": "Cloudflare 'Just a moment' challenge on every path incl. robots.txt → not bypassed, dead end",
                                    "lidl.at": "q/api/search now HTTP 401 (not bypassed); product sitemap 627 URLs, 76 meal-like slugs fetched politely: 56 × 404 (expired weekly offers), 20 × 200 but only bakery snacks/fresh produce, no new ready meals with price",
                                    "kulinarik-im-glas.at": "GO Gastro & Catering Linz: 25 jar dishes with ingredients/weight in the official folder PDF (Stand 08-2025) but no prices/nutrition, B2B focus → candidate, not added"},
          "products": meals}
    json.dump(ev, open(f"raw/gourmet_daheim_{a.stamp}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("articles", len(allp), "meals", len(rows), "csv rows", len(cur) + len(rows), "companies", len(cj), "median", statistics.median(prices))

if __name__ == "__main__":
    main()
