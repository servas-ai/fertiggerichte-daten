"""Sperchenedergut (sperchenedergut.at, Bio-Angus farm Monika und Karl Mayer, Aspach OÖ) → rows 'Online: Sperchenedergut'
in data/online_mealprep.csv (idempotent replace) + company row + logo row + evidence raw/sperchenedergut_<stamp>.json
(Daten-Squad 2026-10-24T1734; candidate noted T0439 as COVERAGE open item 3).
Source: food-connectors `sperchenedergut` adapter (public WooCommerce Store API, robots allow).
Kept 3 heat-up jar meals (330 ml, 9,50 €): Gulaschsuppe, Beuschel, Chili con Carne vom (Bio-)Angusrind.
Excluded: Rinderfond (clear stock), Bolognese (sauce, '300 g entsprechen zwei Personen mit Nudeln als Beilage'), Leberknödel (side/
soup insert), the uncategorised 'Geschenkbox' copies of the same jars, Geschenkboxen, meat cuts, Gutschein, T-Shirts.
No nutrition, GTIN or ingredients published → never estimated; volume only (330 ml) → size_g empty.
Photos: first image = jar packshot on wood with printed dish label (GULASCH / BEUSCHEL / CHILI vom Angusrind, BIO seal on lid) —
vision gate 3/3 PASS (scripts/logo_work_T1734/photo_vision_sheet.jpg).
Shipping: Post-Kühlversand Di–Fr, 9,90 € per cart, free from 150 € (versand page); Austrian Post delivery → Linz covered (shop
does not name a restricted area; basis noted)."""
import sys, json, csv, datetime, argparse
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import sperchenedergut as S

CSV = "data/online_mealprep.csv"; SLUG = "sperchenedergut"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stamp"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    shop = S.store_products()
    kept = [S.to_product(sp).to_dict() for sp in shop if S.is_meal(sp)]
    excluded = [{"id": sp["id"], "name": sp["name"], "categories": [c["name"] for c in sp.get("categories") or []],
                 "reason": "Fond/Sauce/Beilage" if any(c["name"] == "Fertiggerichte" for c in sp.get("categories") or []) else "kein Fertiggericht der Kategorie 'Fertiggerichte' (Fleisch, Geschenkbox-Duplikat, Gutschein, T-Shirt)"}
                for sp in shop if not S.is_meal(sp)]
    rows = []
    for d in kept:
        x = d["extra"]
        rows.append({"name": d["name"], "brand": "Sperchenedergut", "store": S.STORE, "price_eur": d["price_eur"], "size_g": None, "price_per_kg": None,
            "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": "Sperchenedergut Monika und Karl Mayer, Wasserdobl 16, 5251 Aspach (UID ATU76061208)",
            "origin": "AT (Aspach, Bezirk Braunau, OÖ; eigenes Bio-Angusrind lt. Shop)", "bio": bool(x.get("bio_claim")), "veg": None,
            "prep": "erwärmen", "category": "Online Meal-Prep",
            "price_source": f"sperchenedergut.at WooCommerce Store API Preis/Glas inkl. MwSt. {day} (zzgl. 9,90 € Post-Kühlversand, frei ab 150 €)", "price_date": day,
            "nut_source": None, "packaging": f"Glas {int(x['volume_ml'])} ml" if x.get("volume_ml") else "Glas",
            "online": True, "available": bool(x.get("in_stock")), "storage": "Glaskonserve ('Nur durch Erhitzen haltbar gemacht' lt. Shop; Lagerhinweis nicht angegeben)",
            "shelf_life": None, "shipping_eur": 9.9,
            "nut_flag": "keine Nährwerte/Zutaten/GTIN auf sperchenedergut.at (nicht geschätzt); nur Volumen 330 ml → size_g leer; Bio-Kontrollnummer nicht veröffentlicht",
            "ean": None, "portions": 1 if x.get("portion_g") == 300.0 else None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != S.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    vies = json.load(open("/tmp/sp/vies.json"))
    row = {"slug": SLUG, "name": "Sperchenedergut", "role": "producer", "legal_name": "Mayer Karl und Mayer Monika (Sperchenedergut)",
           "lei": None, "register_id": None, "register_authority": None, "fn": None, "legal_form_code": None, "country": "AT",
           "address": "Wasserdobl 16, 5251 Aspach, AT", "entity_status": "UID aktiv (VIES valid); kein Firmenbucheintrag veröffentlicht (landwirtschaftlicher Betrieb)",
           "parent_direct": None, "parent_ultimate": None, "parent_ultimate_lei": None, "founded": None,
           "owners": "Monika und Karl Mayer (lt. Impressum)", "management": None, "employees": None, "revenue": None,
           "website": "https://sperchenedergut.at", "plants": [], "approval_codes": None, "brands": ["Sperchenedergut", "Spercheneder Gut"],
           "chains": [S.STORE], "product_count": len(kept), "median_price_eur": sorted(d["price_eur"] for d in kept)[len(kept)//2], "median_eur_per_10g_protein": None,
           "nace": "Landwirtschaftliche Produktion und Direktvermarktung von Bio-Fleisch sowie Fleischprodukten (Unternehmensgegenstand lt. Impressum)",
           "sources": ["https://sperchenedergut.at/impressum/", "https://ec.europa.eu/taxation_customs/vies/",
                       "https://api.gleif.org/api/v1/lei-records?filter[fulltext]=Sperchenedergut (0 hits)"],
           "gleif_match_score": None, "fetched_at": stamp, "chain_product_count": len(kept), "hrb": None, "former_names": None,
           "registry_status": "verified_vies+impressum (UID ATU76061208 VIES valid, name 'Mayer Karl und Mayer Monika' + address Wasserdobl 16, AT-5251 Aspach = Impressum)",
           "share_capital": None, "register_status": None, "register_entry_date": None, "register_court": None,
           "imprint_url": "https://sperchenedergut.at/impressum/", "uid": "ATU76061208", "uid_vies_name": vies.get("name"),
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
    LR = {"slug": SLUG, "name": "Sperchenedergut", "category": "Markenhersteller", "file": "logos/sperchenedergut.png",
          "source_url": "https://sperchenedergut.at/wp-content/uploads/Spercheneder-Gut-Logo-SCHWARZ.png (homepage logo 1000x500 palette PNG with transparency, robots allow; cropped to the ink bounding box +10 px, otherwise unmodified; vision gate PASS; file staged in fertiggerichte-daten scripts/logo_work_T1734 for the Orchestrator merge)",
          "brands": ["Sperchenedergut", "Spercheneder Gut", S.STORE, "Mayer Karl und Mayer Monika"]}
    LJ = "data/logos.json"; lj = [r for r in json.load(open(LJ)) if r["slug"] != SLUG]; lj.append(LR)
    json.dump(lj, open(LJ, "w"), ensure_ascii=False, indent=1)
    LC = "data/logos.csv"; lc = list(csv.DictReader(open(LC, encoding="utf-8"))); lcols = list(lc[0].keys())
    lc = [r for r in lc if r["slug"] != SLUG]
    with open(LC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lc); w.writerow({k: ("|".join(LR["brands"]) if k == "brands" else LR.get(k, "")) for k in lcols})
    out = {"source": "sperchenedergut.at public WooCommerce Store API (food-connectors sperchenedergut adapter)", "fetched": stamp,
           "robots": "User-agent * disallows only wp-admin, WooCommerce upload/log folders and ?add-to-cart= URLs",
           "operator": {"name": "Sperchenedergut Monika und Karl Mayer", "address": "Wasserdobl 16, 5251 Aspach", "uid": "ATU76061208",
                        "authority": "Bezirkshauptmannschaft Braunau am Inn", "source": "https://sperchenedergut.at/impressum/"},
           "shipping_at": {"source": "https://sperchenedergut.at/versand-und-lieferzeiten-bio-angusrind/",
                           "quote": "Die Versandkosten werden je Warenkorb berechnet und betragen € 9,90. Ab einem Warenkorb von € 150,– versenden wir kostenlos.",
                           "method": "Kühlversand der Post, Zustellung Di–Fr", "fee_eur": 9.9, "free_from_eur": 150.0,
                           "conflict": "some product pages show 'Versandkostenfrei ab € 120,–' in a service box; the shipping page and site banner say 150 € → 150 € used",
                           "delivers_linz": True, "delivers_linz_basis": "Österreichische Post Kühlversand ab Aspach OÖ; no restricted area named"},
           "vision_gate": {"photos": "3/3 PASS (real jar packshots, printed label names the dish, BIO seal on lid)", "logo": "PASS (official homepage logo)"},
           "kept": len(kept), "with_nutrition": 0, "with_gtin": 0, "excluded": excluded, "products": kept, "logo": LR,
           "company_evidence": {"vies": vies, "gleif_fulltext_query": "Sperchenedergut", "gleif_hits": 0}}
    json.dump(out, open(f"raw/sperchenedergut_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("kept", len(kept), "photos", sum(bool(d["image_url"]) for d in kept), "excluded", len(excluded), "csv rows", len(cur) + len(rows), "companies", len(dd), "logos", len(lj))

if __name__ == "__main__":
    main()
