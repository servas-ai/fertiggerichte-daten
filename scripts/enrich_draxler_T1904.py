"""Draxler Geflügel-Wild 'Kulinarik im Glas' (geflügel-draxler.at, Draxler Geflügel-Wild GmbH, Mooskirchen Stmk) → rows
'Online: Draxler Geflügel-Wild' in data/online_mealprep.csv (idempotent replace) + company row + logo row + evidence
raw/draxler_<stamp>.json (Daten-Squad 2026-10-24T1904).
Source: food-connectors `draxler` adapter (public WooCommerce Store API, robots allow; product-page fallback when the API
description belongs to another product — Rehragout on 2026-10-24).
Kept 9 chilled 360 g heat-up jar meals. Excluded: Klare Suppe vom Maishendl (plain broth), Starter Genusspaket (bundle), Gutschein.
No nutrition and no GTIN published → nutrition columns empty, never estimated.
Photos: first image = jar packshot with printed dish label (DRAXLER …) — vision gate 9/9 PASS (scripts/logo_work_T1904/photo_logo_vision_sheet.jpg).
Shipping: within AT by parcel service / Post NEXT DAY FRESH (AGB Stand 01.06.2025, homepage); fee only shown in checkout → shipping_eur empty."""
import sys, json, csv, datetime, argparse
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import draxler as D

CSV = "data/online_mealprep.csv"; SLUG = "draxler-gefluegel-wild"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stamp"); ap.add_argument("--vies", default="/tmp/dxv/vies.json"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = D.store_products()
    kept = [D.to_product(sp).to_dict() for sp in shop if D.is_meal(sp)]
    excluded = [{"id": sp["id"], "slug": sp["slug"], "name": sp["name"],
                 "reason": "klare Brühe" if "klare" in sp["slug"] else "Bundle (Genusspaket)" if "genusspaket" in sp["slug"] else "Gutschein" if "gutschein" in sp["slug"] else "keine Fertiggericht-Kategorie"}
                for sp in shop if not D.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; price = d["price_eur"]
        rows.append({"name": d["name"], "brand": "Draxler Kulinarik im Glas", "store": D.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2), "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": D.PRODUCER, "origin": "AT (Steiermark; eigene Verarbeitung in Mooskirchen lt. Shop)",
            "bio": False, "veg": bool(x.get("vegetarian")), "prep": "im Topf am Herd mit 3 EL Wasser erhitzen (lt. Produktseite)",
            "category": "Online Meal-Prep",
            "price_source": f"geflügel-draxler.at WooCommerce Store API Preis/Glas {day} (zzgl. Versand; Versandkosten nur im Bestellprozess)",
            "price_date": day, "nut_source": None, "packaging": f"Glas {int(size)} g",
            "online": True, "available": bool(x.get("in_stock")), "storage": "gekühlt +4 °C bis +6 °C (durch Erhitzen haltbar gemacht)",
            "shelf_life": None, "shipping_eur": None,
            "nut_flag": "keine Nährwerte und keine GTIN veröffentlicht → nicht geschätzt" + ("; vegan lt. Produktname" if x.get("vegan") else ""),
            "ean": None, "portions": 1})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != D.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    vies = json.load(open(a.vies))
    prices = sorted(d["price_eur"] for d in kept)
    row = {"slug": SLUG, "name": "Draxler Geflügel-Wild", "role": "producer", "legal_name": "Draxler Geflügel-Wild GmbH",
           "lei": "894500FBIXCSSEWGP628", "register_id": "214255g", "register_authority": "Firmenbuch", "fn": "FN 214255g",
           "legal_form_code": "GmbH", "country": "AT", "address": "Kainachstraße 4, 8562 Mooskirchen, AT",
           "entity_status": "eingetragen (Firmenbuch lt. evi.gv.at); LEI LAPSED (entity ACTIVE); UID aktiv (VIES valid)",
           "parent_direct": None, "parent_ultimate": None, "parent_ultimate_lei": None, "founded": "2001-10-11",
           "owners": None,
           "management": "Franz Draxler (Geschäftsführer lt. Impressum); Personen lt. evi.gv.at: Erwin Draxler, Franz Draxler, Marcel Draxler, Maria Nocker, Michael Nocker (Funktion dort nicht angezeigt)",
           "employees": None, "revenue": None, "website": "https://www.geflügel-draxler.at", "plants": [], "approval_codes": None,
           "brands": ["Draxler", "Draxler Kulinarik im Glas", "Draxler Geflügel & Wild"], "chains": [D.STORE],
           "product_count": len(kept), "median_price_eur": prices[len(prices)//2], "median_eur_per_10g_protein": None,
           "nace": "Fleischverarbeitung; Großhandel mit Fleisch, Fleischwaren, Geflügel und Wild; Einzelhandel mit Nahrungs- und Genussmitteln (Geschäftszweig lt. evi.gv.at)",
           "sources": ["https://www.xn--geflgel-draxler-2vb.at/impressum/", "https://www.xn--geflgel-draxler-2vb.at/agb/", "https://www.evi.gv.at/f/214255g",
                       "https://ec.europa.eu/taxation_customs/vies/", "https://api.gleif.org/api/v1/lei-records/894500FBIXCSSEWGP628"],
           "gleif_match_score": 1.0, "fetched_at": stamp, "chain_product_count": len(kept), "hrb": None, "former_names": None,
           "registry_status": "verified_firmenbuch+vies+gleif (FN 214255g evi.gv.at eingetragen seit 11.10.2001, Stammkapital 100 000 €; UID ATU52668607 VIES 'Draxler Geflügel-Wild GmbH', Kainachstraße 4, AT-8562 Mooskirchen = Impressum; LEI 894500FBIXCSSEWGP628 registeredAs 214255g, Registrierung LAPSED)",
           "share_capital": 100000, "register_status": "Eingetragen", "register_entry_date": "2001-10-11", "register_court": None,
           "imprint_url": "https://www.xn--geflgel-draxler-2vb.at/impressum/", "uid": "ATU52668607", "uid_vies_name": vies.get("name"),
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
    LR = {"slug": SLUG, "name": "Draxler Geflügel-Wild", "category": "Markenhersteller", "file": "logos/draxler-gefluegel-wild.png",
          "source_url": "https://www.xn--geflgel-draxler-2vb.at/wp-content/uploads/2021/10/draxler-logo.svg (site header logo SVG, robots allow; rendered to PNG 800x584 with cairosvg, transparent background, otherwise unmodified; vision gate PASS; files staged in fertiggerichte-daten scripts/logo_work_T1904 for the Orchestrator merge)",
          "brands": ["Draxler", "Draxler Kulinarik im Glas", D.STORE, "Draxler Geflügel-Wild GmbH"]}
    LJ = "data/logos.json"; lj = [r for r in json.load(open(LJ)) if r["slug"] != SLUG]; lj.append(LR)
    json.dump(lj, open(LJ, "w"), ensure_ascii=False, indent=1)
    LC = "data/logos.csv"; lc = list(csv.DictReader(open(LC, encoding="utf-8"))); lcols = list(lc[0].keys())
    lc = [r for r in lc if r["slug"] != SLUG]
    with open(LC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lc); w.writerow({k: ("|".join(LR["brands"]) if k == "brands" else LR.get(k, "")) for k in lcols})
    out = {"source": "geflügel-draxler.at public WooCommerce Store API (food-connectors draxler adapter)", "fetched": stamp,
           "robots": "User-agent * disallows only wc-logs, WooCommerce transient uploads and ?add-to-cart= URLs",
           "operator": {"name": "Draxler Geflügel-Wild GmbH", "address": "Kainachstraße 4, 8562 Mooskirchen", "fn": "214255g",
                        "uid": "ATU52668607", "lei": "894500FBIXCSSEWGP628", "md": "Franz Draxler", "source": "https://www.xn--geflgel-draxler-2vb.at/impressum/"},
           "shipping": {"source": "https://www.xn--geflgel-draxler-2vb.at/agb/ (Stand 01.06.2025) + homepage", "countries": ["AT"],
                        "carrier": "Österreichische Post NEXT DAY FRESH (Lebensmittelzustellung) österreichweit", "fees": None,
                        "fees_note": "Versandkosten werden im Bestellprozess gesondert ausgewiesen (AGB §3) — not read, no cart/checkout used",
                        "delivers_linz": True, "delivers_linz_basis": "Lieferung an Adressen innerhalb Österreichs (AGB), 'ÖSTERREICHWEIT' (Startseite)"},
           "vision_gate": {"photos": "9/9 PASS (jar packshots, printed DRAXLER label names the dish)", "logo": "PASS (official header logo: deer + DRAXLER GEFLÜGEL & WILD wordmark)"},
           "kept": len(kept), "with_nutrition": 0, "with_gtin": 0, "excluded": excluded, "products": kept, "logo": LR,
           "company_evidence": {"vies": vies, "evi": "https://www.evi.gv.at/f/214255g (Status Eingetragen, Eintragungsdatum 11.10.2001, Stammkapital EUR 100 000, Geschäftszweig Fleischverarbeitung …)",
                                "gleif": {"lei": "894500FBIXCSSEWGP628", "status": "LAPSED", "entity_status": "ACTIVE", "registeredAs": "214255g",
                                          "ultimate_parent_exception": "NATURAL_PERSONS"}}}
    json.dump(out, open(f"raw/draxler_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("kept", len(kept), "excluded", len(excluded), "csv rows", len(cur) + len(rows), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows), "companies", len(dd), "logos", len(lj))

if __name__ == "__main__":
    main()
