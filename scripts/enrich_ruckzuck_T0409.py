"""Ruck Zuck Laden — Dunzinger's Ruck Zuck Glasl (ruckzuck-laden.at, Schimpl OG, Hirschbach im Mühlkreis OÖ)
→ evidence raw/ruckzuck_<stamp>.json + rows 'Online: Ruck Zuck Laden (Dunzinger's)' in data/online_mealprep.csv
(idempotent replace) + company row + logo row (Daten-Squad 2026-10-18T0409; probe in raw/ruckzuck_probe_2026-10-18T0311.json).

Source: food-connectors `ruckzuck` adapter — WP sitemap wp-sitemap-ecstore-1.xml (17 product ids) → public Ecwid storefront
JSON (POST eu-fra4-storefront-api.ecwid.com/storefront/api/v1/102929329/catalog/product, the shop widget's own unauthenticated
call). robots: site disallows only /wp-admin/, API host no robots.txt. Polite gate 1 req/s, no login/cookies/cart.
Kept = 7 heat-up jar meals; excluded: 2 clear broths (1 l, 'OHNE Einlage'), Sugo Bolognese + Pastasoße (sauces), Apfel-Rotkraut
(side), Gulaschsaft (sauce), 3 Kekse, Hallo Baby Box (baby gift box — baby food never staged).
No nutrition and no GTIN published (SKUs are internal) → never estimated; volume only for Erdäpfelgulasch (315 ml) → size_g empty.
Photos: the jar packshot (white background, printed dish label) — vision-gated 7/7 PASS (scripts/logo_work_T0409/photo_vision_sheet.jpg).
The main 'serving' images were rejected as product photos (photorealistic illustrations; e.g. Chili con Carne shows cheese/carrot
cubes that are not in the recipe and a malformed chili slice) and are kept only in the evidence as serving_image_url.
Usage: python3 scripts/enrich_ruckzuck_T0409.py [--stamp 2026-10-18T0409]"""
import sys, json, csv, time, datetime, argparse, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import ruckzuck as R
from food_connectors.http import UA

CSV = "data/online_mealprep.csv"
OPERATOR = {"name": "Schimpl OG", "seat": "Guttenbrunn 18, 4242 Hirschbach im Mühlkreis (AT, OÖ; ~25 km nördlich von Linz)",
            "register": "FN 306047w (Landesgericht Linz) — evi.gv.at: Eingetragen, Offene Gesellschaft, Eintragungsdatum 08.03.2008, Geschäftszweig 'Betrieb eines Gasthauses'",
            "vat": "ATU64017307 (VIES valid 2026-10-18, name 'Schimpl OG' + address 'Guttenbrunn 18, AT-4242 Hirschbach/Mühlkreis')", "lei": None,
            "partners": "2 unbeschränkt haftende Gesellschafter lt. evi.gv.at (Gerald Schimpl, Carolin Schimpl, eingetragen 31.10.2014)",
            "trade_names": "Ruck Zuck Laden, Dunzinger's Ruck Zuck Glasl; Kontakt-E-Mail @kraeuterwirt.at",
            "source": "https://www.ruckzuck-laden.at/impressum/"}
SHIPPING = {"source": "https://www.ruckzuck-laden.at/ (Startseite 'Direkt zu DIR nach Hause')",
            "quote": "Wir liefern unsere Gläser direkt zu dir nach Hause Österreich ab 100 Euro in Deutschland ab 150 Euro ohne Versandkosten ansonsten 15 Euro",
            "fee_eur": 15.0, "free_from_eur_at": 100.0, "area": "Österreich und Deutschland",
            "delivers_linz": True, "delivers_linz_basis": "Lieferung nach ganz Österreich lt. Startseite"}
VISION = {"rule": "jar packshot of that article shows the Dunzinger's Ruck Zuck jar whose printed label names the dish",
          "pass": "7/7 (Gemüse-Linsen-Eintopf, Rindsgulasch, Erdäpfel-Gulasch, Curry mit Huhn, Chili con carne, würziges Curry, 'Ragout Mühlviertler Rindvieh' = Rinder-Ragout)",
          "rejected_as_product_photo": "main serving images (6/7 photorealistic illustrations without pack; Gulasch vom Rind main = real plated photo but no pack) → kept as serving_image_url only"}


def get_ok(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=25) as r:
            b = r.read(65536); return r.status if b[:3] == b"\xff\xd8\xff" else f"{r.status} not-jpeg"
    except Exception as e:
        return getattr(e, "code", None) or repr(e)[:60]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stamp"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    tiles = R.RuckZuck().tiles(); kept, excluded = [], []
    for t in tiles:
        p = R.parse_product(R.product_json(t["id"]), t["url"])
        if not p: excluded.append({"id": t["id"], "reason": "not found"}); continue
        if not R.is_meal_name(p.name):
            excluded.append({"id": p.source_id, "name": p.name, "price_eur": p.price_eur, "reason": "kein Fertiggericht (Suppe ohne Einlage/Soße/Beilage/Kekse/Baby-Box)"}); continue
        d = p.to_dict(); d["extra"]["image_get"] = get_ok(p.image_url) if p.image_url else None; time.sleep(0.5)
        d["extra"]["vision_gate"] = "PASS (jar packshot, label matches)" if d["extra"]["image_get"] == 200 else "no image"
        if d["extra"]["image_get"] != 200: d["image_url"] = None
        kept.append(d)
    rows = []
    for d in kept:
        x = d["extra"]
        veg = "vegan" if x.get("vegan") else None
        name = d["name"].replace(" VEGAN", "").strip()
        rows.append({"name": name, "brand": "Dunzinger's Ruck Zuck", "store": R.STORE, "price_eur": d["price_eur"], "size_g": None, "price_per_kg": None,
            "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": "Schimpl OG, Guttenbrunn 18, 4242 Hirschbach im Mühlkreis, FN 306047w",
            "origin": "AT (Hirschbach im Mühlkreis, OÖ; Fleisch ausschließlich aus Österreich lt. Shop)", "bio": False, "veg": veg,
            "prep": None, "category": "Online Meal-Prep",
            "price_source": f"ruckzuck-laden.at Ecwid-Storefront Preis/Glas inkl. 10 % MwSt. {day} (zzgl. 15 € Versand AT, frei ab 100 €)", "price_date": day,
            "nut_source": None, "packaging": f"Glas {int(x['volume_ml'])} ml (im Glas eingekocht)" if x.get("volume_ml") else "Glas (im Glas eingekocht)",
            "online": True, "available": not x.get("sold_out"), "storage": "ungekühlt (Glaskonserve)", "shelf_life": "lange ungekühlt haltbar lt. Shop (kein Datum angegeben)",
            "shipping_eur": 15.0, "nut_flag": "keine Nährwertangabe auf ruckzuck-laden.at (nicht geschätzt); keine Nettofüllmenge außer Erdäpfelgulasch 315 ml → size_g leer",
            "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != R.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    SLUG = "schimpl-og"
    prices = sorted(d["price_eur"] for d in kept)
    row = {"slug": SLUG, "name": "Dunzinger's Ruck Zuck (Schimpl OG)", "role": "producer", "legal_name": "Schimpl OG",
           "lei": None, "register_id": "306047w", "register_authority": None, "fn": "FN 306047w", "legal_form_code": None, "country": "AT",
           "address": "Guttenbrunn 18, 4242 Hirschbach im Mühlkreis, AT", "entity_status": "Eingetragen (Firmenbuch, evi.gv.at)",
           "parent_direct": None, "parent_ultimate": None, "parent_ultimate_lei": None, "founded": "2008-03-08",
           "owners": "2 unbeschränkt haftende Gesellschafter (natürliche Personen: Gerald Schimpl, Carolin Schimpl lt. evi.gv.at)",
           "management": "Gerald Schimpl, Carolin Schimpl (unbeschränkt haftende Gesellschafter lt. evi.gv.at)", "employees": None, "revenue": None,
           "website": "https://www.ruckzuck-laden.at", "plants": [], "approval_codes": None, "brands": ["Dunzinger's", "Dunzinger's Ruck Zuck", "Ruck Zuck Glasl"],
           "chains": ["Ruck Zuck Laden"], "product_count": len(kept), "median_price_eur": prices[len(prices)//2], "median_eur_per_10g_protein": None,
           "nace": "Betrieb eines Gasthauses (Geschäftszweig lt. Firmenbuch)",
           "sources": ["https://www.ruckzuck-laden.at/impressum/", "https://ec.europa.eu/taxation_customs/vies/", "https://www.evi.gv.at/f/306047w",
                       "https://api.gleif.org/api/v1/lei-records?filter[fulltext]=Schimpl OG (0 hits)"],
           "gleif_match_score": None, "fetched_at": stamp, "chain_product_count": len(kept),
           "registry_status": "verified_vies+impressum+firmenbuch (Impressum FN 306047w = evi.gv.at; VIES name+address match)",
           "founded_source": "Firmenbuch Eintragungsdatum 08.03.2008 (evi.gv.at/f/306047w) — legal entity (Gasthaus operator), not the jar brand",
           "share_capital": None, "register_status": "Eingetragen", "register_entry_date": "2008-03-08", "register_court": "Landesgericht Linz",
           "imprint_url": "https://www.ruckzuck-laden.at/impressum/", "uid": "ATU64017307", "uid_vies_name": "Schimpl OG",
           "uid_vies_address": "Guttenbrunn 18, AT-4242 Hirschbach/Mühlkreis", "uid_checked_at": "2026-10-18T04:11:38Z"}
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
    LR = {"slug": "ruckzuck", "name": "Dunzinger's Ruck Zuck", "category": "Handelskette", "file": "logos/ruckzuck.png",
          "source_url": "https://www.ruckzuck-laden.at/wp-content/uploads/go-x/u/9d9942be-6306-4f5a-92d7-89655b8772a7/image.png (ruckzuck-laden.at header logo 455x448 RGBA, robots allow; cropped to 455x411 to drop a cut-off fragment below the pot; same emblem as on the jar labels; vision gate PASS; file staged in fertiggerichte-daten scripts/logo_work_T0409 for the Orchestrator merge)",
          "brands": ["Dunzinger's", "Dunzinger's Ruck Zuck", "Ruck Zuck Laden", R.STORE, "Schimpl OG"]}
    LJ = "data/logos.json"; lj = [r for r in json.load(open(LJ)) if r["slug"] != "ruckzuck"]; lj.append(LR)
    json.dump(lj, open(LJ, "w"), ensure_ascii=False, indent=1)
    LC = "data/logos.csv"; lc = list(csv.DictReader(open(LC, encoding="utf-8"))); lcols = list(lc[0].keys())
    lc = [r for r in lc if r["slug"] != "ruckzuck"]
    with open(LC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lc); w.writerow({**LR, "brands": "|".join(LR["brands"])})
    out = {"source": "ruckzuck-laden.at WP store sitemap + public Ecwid storefront JSON (food-connectors ruckzuck adapter)", "fetched": stamp,
           "robots": "www.ruckzuck-laden.at: User-agent * Disallow /wp-admin/ only; eu-fra4-storefront-api.ecwid.com: no robots.txt (404 → allow)",
           "operator": OPERATOR, "shipping_at": SHIPPING, "vision_gate": VISION, "sitemap_products": len(tiles), "kept": len(kept),
           "with_nutrition": 0, "with_gtin": 0, "excluded": excluded, "products": kept, "logo": LR,
           "company_evidence": {"vies": json.load(open("/tmp/rz/vies.json")), "gleif_fulltext_query": "Schimpl OG", "gleif_hits": 0,
                                "evi_extract": {"Status": "Eingetragen", "Firmenbuchnummer": "306047w", "Adresse": "Guttenbrunn 18, 4242 Hirschbach im Mühlkreis",
                                                "Eintragungsdatum": "08.03.2008", "Rechtsform": "Offene Gesellschaft", "Geschäftszweig": "Betrieb eines Gasthauses",
                                                "Unbeschränkt haftende Gesellschafter/in": "2 Personen (Gerald Schimpl, Carolin Schimpl; eingetragen 31.10.2014)"}}}
    json.dump(out, open(f"raw/ruckzuck_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("sitemap", len(tiles), "kept", len(kept), "photos", sum(bool(d["image_url"]) for d in kept), "excluded", len(excluded),
          "csv rows", len(cur) + len(rows), "companies", len(dd), "logos", len(lj))

if __name__ == "__main__":
    main()
