"""ADAMAH BioHof (adamah.at, Glinzendorf/Marchfeld) — ready meals of the Bio-Shop → evidence raw/adamah_<stamp>.json
+ rows 'Online: ADAMAH BioHof' in data/online_mealprep.csv (idempotent replace) + operator company row
(Daten-Squad 2026-10-17T2102).

Source: food-connectors `adamah` adapter — the Angular shop's own anonymous product JSON: POST /ACM/api/webshop/getproducts
(searchCriteria, union over adapter SEARCH_TERMS) → candidates; categories 0841 'Fertiggerichte' / 0275 'gekühlte
Fertiggerichte' + adapter meal filter (sauces/Sugo, Pasteten/Aufstriche, raw pasta, patties, desserts, broth excluded with
reason) → POST getproductdetail (Zutaten, description). robots.txt `User-agent: * Allow: /`. No login/cookies/cart/user calls,
≥1 s per request. adamah.at publishes no nutrition and no GTIN (eanCode = internal PLU) → never estimated.
Photos: official AttachmentLoader images (GET 200), vision-gated by the Daten-Squad (contact sheet).
Usage: python3 scripts/enrich_adamah.py --cache raw/adamah_2026-10-17T2102 [--stamp 2026-10-17T2102]"""
import sys, os, json, csv, argparse, statistics
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import adamah as A

CSV = "data/online_mealprep.csv"
OPERATOR = {"name": "ADAMAH Vertriebs GmbH", "brand": "ADAMAH BioHof", "seat": "Sonnenweg 11, 2280 Glinzendorf (AT)",
            "register": "FN 554551t (Landesgericht Korneuburg), eingetragen 15.05.2021, Stammkapital EUR 35 000",
            "vat": "ATU76911656 (VIES valid 2026-10-17T21:31Z, name 'ADAMAH Vertriebs GmbH' + address 'Sonnenweg 11, AT-2280 Glinzendorf' match)",
            "lei": None, "gleif": "fulltext 'adamah' → only ADAMAH Grenoble FR (unrelated) → no LEI",
            "owners": "Zoubek Beteiligungs GmbH (1 Gesellschafter/in lt. evi.gv.at)", "management": "Elisabeth Zoubek (Geschäftsführerin lt. Firmenbuch, vertritt seit 27.07.2021)",
            "bio_control": "AT-BIO-301", "sources": ["https://www.evi.gv.at/f/554551t", "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/AT/vat/U76911656",
            "https://www.adamah.at/AGB (FN + UID as printed)", "https://adamah.markt.abhofladen.at/impressum (Impressum mirror: FN + UID)"]}
SHIPPING = {"area": "Wien, Teile Niederösterreichs und des Burgenlands (BioKistl-Zustellung; nicht Linz)",
            "source": "konsument.at Kochbox-Test 2023 (https://konsument.at/kochbox-test-2023) via food-connectors mealkits registry",
            "fee": None, "fee_note": "Liefergebühr/Mindestbestellwert nicht aus einer abrufbaren adamah.at-Seite gelesen (SPA) → shipping_eur leer",
            "delivers_linz": False}
EXCLUDED_REASON = [("sugo|sauce|soße", "Sauce/Sugo, kein Fertiggericht"), ("pastete|rillettes|aufstrich", "Pastete/Aufstrich"),
                   ("burger|schnitzel|faschier|grünkern|lupinen|falafel|taler", "Fleischersatz-/Bratling-Komponente"),
                   ("tortellini|ravioli|nockerl", "frische Pasta/Teigware (Beilage)"), ("cheesecake|scheiterhaufen", "Süßspeise/Dessert"),
                   ("semmelrolle|grillinge|bohnen gegart", "Beilage/Grundprodukt"), ("klare suppe|brüh|würfel|paste", "Brühe/Würze")]
VISION = {"rule": "official adamah.at product photo for that sid shows the named product (pack/jar with legible label or the dish of the named kind)",
          "pass": ["11257", "11287", "67253", "42088", "42089", "42090", "42091", "42092", "42093", "42094", "42095", "67000", "67248", "67254", "67256",
                   "67257", "67258", "68694", "68790", "68890", "69021", "70140", "70141", "70226", "70905", "71496", "71497"],
          "weak": {"68890": "Wildragout: plated serving photo with gnocchi (no jar shown)", "70226": "Kaspressknödel: plated in soup (serving suggestion, no pack)",
                   "68694": "Joseph Brot Linseneintopf: Weck jar, hang-tag text not legible at 400 px", "71496": "GAIA Lasagne: styled jar photo, label not legible"}}

def reason(name):
    import re
    for pat, r in EXCLUDED_REASON:
        if re.search(pat, name, re.I): return r
    return "kein Fertiggericht-Name / andere Kategorie"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache", required=True); ap.add_argument("--stamp", default="2026-10-17T2102"); a = ap.parse_args()
    cands = json.load(open(os.path.join(a.cache, "search_candidates.json"), encoding="utf-8"))
    inmeal = [p for p in cands if p.get("category") in A.MEAL_CATEGORIES]
    kept, excluded = [], []
    for p in sorted(inmeal, key=lambda p: p["sid"]):
        if not A.is_meal(p):
            excluded.append({"sid": p["sid"], "name": p["name"], "producer": p.get("producer"), "price_eur": A.price(p), "reason": reason(p["name"])}); continue
        f = os.path.join(a.cache, f"d_{p['sid']}.json")
        d = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else (A.detail_raw(p["sid"]) or p)
        prod = A.to_product(d).to_dict(); sid = prod["source_id"]
        prod["extra"]["image_get"] = 200 if sid in VISION["pass"] else None
        prod["extra"]["vision_gate"] = ("PASS" + (f" (weak: {VISION['weak'][sid]})" if sid in VISION["weak"] else "")) if sid in VISION["pass"] else "not checked"
        if not prod["extra"]["vision_gate"].startswith("PASS"): prod["image_url"] = None
        kept.append(prod)
    prices = [k["price_eur"] for k in kept if k["price_eur"]]
    out = {"source": "adamah.at Bio-Shop — POST /ACM/api/webshop/getproducts + getproductdetail (food-connectors adamah adapter)", "fetched": a.stamp,
           "robots": "User-agent: * Allow: / (Sitemap: /sitemap.xml)", "operator": OPERATOR, "delivery": SHIPPING, "vision_gate": VISION,
           "search_terms": A.SEARCH_TERMS + ["Gericht", "Pizza", "Strudel", "Laibchen", "Risotto", "Moussaka", "Dal", "Gemüsepfanne", "Scheiterhaufen", "Gröstl", "Rouladen", "Kürbis"],
           "candidates": len(cands), "in_meal_categories": len(inmeal), "kept": len(kept), "with_nutrition": 0,
           "median_price_eur": statistics.median(prices) if prices else None, "excluded": excluded, "products": kept,
           "notes": ["Biohof Achleitner jars also sold here (6 rows): adamah.at lists 410 ml = jar volume → size empty (biohof.at: content ca. 350 ml)",
                     "Hartls Kulinarikum (Linz) Weckglas meals 460 g are the same producer as the myProduct rows (other store, other price)",
                     "Venatio wild dishes are 'nicht bio - Wild mit BioZutaten' (bio=false)",
                     "Search-based enumeration (the shop has no public category JSON without product-group ids); items not matching any search term may be missing"]}
    json.dump(out, open(f"raw/adamah_{a.stamp}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    day = a.stamp[:10]; rows = []
    for d in kept:
        x, size, price = d["extra"], d["size_g"], d["price_eur"]
        pfand = "Pfand" in (d["name"] or "") or "Weck" in (d["name"] or "") or "Glas" in (x.get("unit_desc") or "")
        rows.append({"name": d["name"], "brand": d["brand"], "store": A.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2) if size and price else None, "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": d["producer"], "origin": d["origin"], "bio": x.get("bio") is True,
            "veg": "vegan" if "vegan" in (d["name"] or "").lower() else None, "prep": None, "category": "Online Meal-Prep",
            "price_source": f"adamah.at Bio-Shop Preis je Stück inkl. MwSt. {day} (BioKistl-Lieferung Wien/NÖ/Burgenland)", "price_date": day,
            "nut_source": None, "packaging": "Glas (Pfand/Weck)" if pfand else None, "online": True,
            "available": not x.get("currently_not_available"), "storage": "gekühlt" if d["category"] == "gekühlte Fertiggerichte" else None,
            "shelf_life": None, "shipping_eur": None,
            "nut_flag": "keine Nährwertangabe auf adamah.at (nicht geschätzt)" + (f"; Menge: {x['size_note']}" if x.get("size_note") and "Glasvolumen" in x["size_note"] else ""),
            "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != A.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    print("candidates", len(cands), "in_cat", len(inmeal), "kept", len(kept), "photos", sum(bool(d["image_url"]) for d in kept),
          "excluded", len(excluded), "median", out["median_price_eur"], "csv rows", len(cur) + len(rows))

if __name__ == "__main__":
    main()
