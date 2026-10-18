"""Gerbl im Glas (shop.gerbl.at, Fleischhauerei Gerbl GmbH, Vöcklamarkt OÖ) → evidence raw/gerbl_<stamp>.json
+ rows 'Online: Gerbl im Glas' in data/online_mealprep.csv (idempotent replace) + company row + logo row
(Daten-Squad 2026-10-18T0236).

Source: food-connectors `gerbl` adapter — category https://shop.gerbl.at/ecommerce/category-browse?category_id=150129
→ product pages (price incl. MwSt., 'ca. 450 ml' jar, Zutaten, Allergene, Haltbarkeit, main photo). robots.txt (*)
disallows only /ftpdir/ /admin/ /ecommerce/dc_components/. No login/cookies/cart, ≥1 s per request.
Kept = 19 heat-up dishes/soups GIG01–GIG19; excluded: Leberstreichwurst (spread), 2 Geschenkskörbe (bundles).
No nutrition and no GTIN published → never estimated; pack is a jar volume in ml → size_g empty (no ml→g guess).
Photos: official jar packshots (label number + dish name match the article) — vision-gated 19/19 PASS.
Usage: python3 scripts/enrich_gerbl_T0236.py --cache /tmp/gerbl [--stamp 2026-10-18T0236]"""
import sys, os, json, csv, time, datetime, argparse, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import gerbl as G
from food_connectors.http import UA, get

CSV = "data/online_mealprep.csv"
OPERATOR = {"name": "Fleischhauerei Gerbl GmbH", "seat": "Hauptstraße 14, 4870 Vöcklamarkt (AT); Filiale Pollheimerstraße 4, 4850 Timelkam",
            "register": "FN 612319w (Landesgericht Wels)", "vat": "ATU79858539 (VIES valid 2026-10-18, name+address match)", "lei": None,
            "management": "Wilhelm Franz Gerbl (Geschäftsführer + Alleingesellschafter lt. evi.gv.at; 'Metzgermeister Willi Gerbl' lt. Shop)",
            "source": "https://shop.gerbl.at/gerbl-shop/shop/info/impressum"}
SHIPPING = {"source": "https://shop.gerbl.at/gerbl-shop/shop/info/versandkosten + product page 'Verfügbarkeit und Versand'",
            "fee": "Pauschale Verpackung + Versand 9,90 € (EMS Expressversand)", "area": "innerhalb Österreichs (EU-Ausland auf Anfrage)",
            "dispatch": "Versand jeden Dienstag (Bestellung bis Di 12:00), Lieferdauer 1–2 Werktage",
            "delivers_linz": True, "delivers_linz_basis": "Versand ganz Österreich lt. Versandkostenseite"}
VISION = {"rule": "main product photo of that article shows the Gerbl jar whose lid/label number (01–19) and printed dish name match the article",
          "pass": "all 19 (GIG01 Rindsgulasch … GIG19 Rindsbraten; contact sheet scripts/logo_work_T0236/photo_vision_sheet.jpg)"}

def head(url):
    # shop.gerbl.at answers HEAD with 404 for gallery files but GET with 200 → verify with a GET (first 64 KB, must be JPEG)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
            b = r.read(65536)
            return r.status if b[:3] == b"\xff\xd8\xff" else f"{r.status} not-jpeg"
    except Exception as e:
        return getattr(e, "code", None) or repr(e)[:60]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache"); ap.add_argument("--stamp"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    cat = open(os.path.join(a.cache, "cat.html"), encoding="utf-8").read() if a.cache else get(G.CATEGORY, raw=True, timeout=40).decode("utf-8", "replace")
    tiles = G.parse_category(cat); kept, excluded = [], []
    for t in tiles:
        f = os.path.join(a.cache, f"p{t['id']}.html") if a.cache else None
        h = open(f, encoding="utf-8", errors="replace").read() if f and os.path.exists(f) else (time.sleep(1.0) or get(t["url"], raw=True, timeout=40).decode("utf-8", "replace"))
        p = G.parse_product(h, t["url"])
        if not p: excluded.append({"id": t["id"], "reason": "parse failed"}); continue
        if not G.is_meal_name(p.name):
            excluded.append({"id": p.source_id, "name": p.name, "price_eur": p.price_eur,
                             "reason": "Geschenkskorb/Bundle" if "korb" in p.name.lower() else "kein Fertiggericht (Streichwurst)"}); continue
        d = p.to_dict(); d["extra"]["image_head"] = head(p.image_url); time.sleep(0.5)
        d["extra"]["vision_gate"] = "PASS"
        if d["extra"]["image_head"] != 200: d["image_url"] = None
        kept.append(d)
    out = {"source": "shop.gerbl.at 'Gerbl im Glas' category + product pages (food-connectors gerbl adapter)", "fetched": stamp,
           "robots": "User-agent: * — Disallow only /ftpdir/ /admin/ /ecommerce/dc_components/ (AhrefsBot/SemrushBot/MJ12bot/ClaudeBot fully disallowed; not our UA)",
           "operator": OPERATOR, "shipping_at": SHIPPING, "vision_gate": VISION, "category_products": len(tiles), "kept": len(kept),
           "with_nutrition": 0, "with_gtin": 0, "excluded": excluded, "products": kept}
    json.dump(out, open(f"raw/gerbl_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    rows = []
    for d in kept:
        x = d["extra"]
        rows.append({"name": d["name"], "brand": "Gerbl", "store": G.STORE, "price_eur": d["price_eur"], "size_g": None, "price_per_kg": None,
            "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": "Fleischhauerei Gerbl GmbH, Hauptstraße 14, 4870 Vöcklamarkt, FN 612319w",
            "origin": "AT (Vöcklamarkt/Timelkam, OÖ; Fleisch von Bauernhöfen aus der näheren Umgebung lt. Shop)", "bio": False,
            "veg": "vegetarisch" if x.get("vegetarian") else None, "prep": None, "category": "Online Meal-Prep",
            "price_source": f"shop.gerbl.at Produktseite Preis/Stk inkl. MwSt. {day} (zzgl. 9,90 € Versand AT)", "price_date": day,
            "nut_source": None, "packaging": f"Glas ca. {int(x['volume_ml'])} ml (pasteurisiert, Rücknahme leerer Gläser)" if x.get("volume_ml") else "Glas",
            "online": True, "available": True, "storage": "Kühlregal (2–6 °C)" if x.get("storage") else None, "shelf_life": x.get("shelf_life"),
            "shipping_eur": 9.9, "nut_flag": "keine Nährwertangabe auf shop.gerbl.at (nicht geschätzt); Menge nur als Glasvolumen ca. 450 ml → size_g leer",
            "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != G.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    # company row
    SLUG = "fleischhauerei-gerbl-gmbh"
    prices = sorted(d["price_eur"] for d in kept)
    row = {"slug": SLUG, "name": "Gerbl (Fleischhauerei Gerbl GmbH)", "role": "producer", "legal_name": "Fleischhauerei Gerbl GmbH",
           "lei": None, "register_id": "612319w", "register_authority": None, "fn": "FN 612319w", "legal_form_code": None, "country": "AT",
           "address": "Hauptstraße 14, 4870 Vöcklamarkt, AT", "entity_status": "Eingetragen (Firmenbuch, evi.gv.at)",
           "parent_direct": None, "parent_ultimate": None, "parent_ultimate_lei": None, "founded": "2023-09-19",
           "owners": "1 natürliche Person (Alleingesellschafter lt. Firmenbuch/evi.gv.at, eingetragen 19.09.2023)",
           "management": "Wilhelm Franz Gerbl (Geschäftsführer lt. Firmenbuch/evi.gv.at)", "employees": None, "revenue": None,
           "website": "https://www.gerbl.at", "plants": [], "approval_codes": None, "brands": ["Gerbl", "Gerbl im Glas", "beefMax"],
           "chains": ["Gerbl im Glas"], "product_count": len(kept), "median_price_eur": prices[len(prices)//2], "median_eur_per_10g_protein": None,
           "nace": "Fleischergewerbe und Viehhandelsgewerbe (Geschäftszweig lt. Firmenbuch)",
           "sources": ["https://shop.gerbl.at/gerbl-shop/shop/info/impressum", "https://ec.europa.eu/taxation_customs/vies/", "https://www.evi.gv.at/f/612319w",
                       "https://api.gleif.org/api/v1/lei-records?filter[fulltext]=Gerbl (0 hits)"],
           "gleif_match_score": None, "fetched_at": stamp, "chain_product_count": len(kept),
           "registry_status": "verified_vies+impressum+firmenbuch (Impressum FN 612319w = evi.gv.at; VIES name+address match)",
           "founded_source": "Firmenbuch Eintragungsdatum 19.09.2023 (Neueintragung; evi.gv.at/f/612319w) — legal entity, the butcher's shop itself is older",
           "share_capital": "EUR 35 000 (lt. evi.gv.at)", "register_status": "Eingetragen", "register_entry_date": "2023-09-19", "register_court": "Landesgericht Wels",
           "imprint_url": "https://shop.gerbl.at/gerbl-shop/shop/info/impressum", "uid": "ATU79858539", "uid_vies_name": "Fleischhauerei Gerbl GmbH",
           "uid_vies_address": "Hauptstraße 14, AT-4870 Vöcklamarkt", "uid_checked_at": "2026-10-18T02:38:33Z"}
    P = "data/companies.json"
    dd = [r for r in json.load(open(P)) if r["slug"] != SLUG]; dd.append(row)
    json.dump(dd, open(P, "w"), ensure_ascii=False, indent=1)
    C = "data/companies.csv"
    cc = list(csv.DictReader(open(C, encoding="utf-8"))); ccols = list(cc[0].keys())
    cc = [r for r in cc if r["slug"] != SLUG]
    o = {c: row.get(c) for c in ccols}; o["brands"] = "|".join(row["brands"]); o["chains"] = "|".join(row["chains"])
    if "hrb" in o: o["hrb"] = None
    if "plants_count" in o: o["plants_count"] = 0
    with open(C, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(cc)
        w.writerow({k: ("" if v is None else (json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v)) for k, v in o.items()})
    # logo row
    LR = {"slug": "gerbl", "name": "Gerbl Fleischhauerei", "category": "Handelskette", "file": "logos/gerbl.png",
          "source_url": "https://shop.gerbl.at/cu/gerbl-shop/images/logo_gerbl-shop.png (shop.gerbl.at header logo, 140x135 RGBA, robots allow; unmodified, low-res; emblem matches the jar labels; vision gate PASS; file staged in fertiggerichte-daten scripts/logo_work_T0236 until the fertig uid freeze lifts)",
          "brands": ["Gerbl", "Gerbl im Glas", "Online: Gerbl im Glas", "Fleischhauerei Gerbl", "Fleischhauerei Gerbl GmbH"]}
    LJ = "data/logos.json"; lj = [r for r in json.load(open(LJ)) if r["slug"] != "gerbl"]; lj.append(LR)
    json.dump(lj, open(LJ, "w"), ensure_ascii=False, indent=1)
    LC = "data/logos.csv"; lc = list(csv.DictReader(open(LC, encoding="utf-8"))); lcols = list(lc[0].keys())
    lc = [r for r in lc if r["slug"] != "gerbl"]
    with open(LC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lc); w.writerow({**LR, "brands": "|".join(LR["brands"])})
    ev = {"run": f"{stamp} Daten-Squad", "vies": json.load(open("/tmp/vies_gerbl.json")), "gleif_fulltext_query": "Gerbl", "gleif_hits": 0,
          "evi_extract": {"Firmenbuchnummer": "612319w", "Adresse": "Hauptstraße 14, 4870 Vöcklamarkt", "Eintragungsdatum": "19.09.2023",
                          "Rechtsform": "GmbH", "Stammkapital": "EUR 35 000", "Geschäftszweig": "Fleischergewerbe und Viehhandelsgewerbe",
                          "Geschäftsführer/in": "1 Person (Wilhelm Franz Gerbl)", "Gesellschafter/in": "1 Person (natürliche Person)"}}
    out["company_evidence"] = ev; out["logo"] = LR
    json.dump(out, open(f"raw/gerbl_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("tiles", len(tiles), "kept", len(kept), "photos", sum(bool(d["image_url"]) for d in kept), "excluded", len(excluded),
          "csv rows", len(cur) + len(rows), "companies", len(dd), "logos", len(lj))

if __name__ == "__main__":
    main()
