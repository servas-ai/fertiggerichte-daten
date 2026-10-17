"""Biohof Achleitner (biohof.at, Eferding OÖ) — 'Hausg'mocht Speisen' → evidence raw/biohof_achleitner_<stamp>.json
+ rows 'Online: Biohof Achleitner' in data/online_mealprep.csv (idempotent replace) (Daten-Squad 2026-10-17T0502).

Source: food-connectors `biohof-achleitner` adapter — category https://www.biohof.at/hausgmocht-speisen (server-rendered
tiles) → product pages (Füllmenge, Zubereitung, Zutaten, price incl. MwSt., og:image). robots.txt (*) Allow: / and
disallows only /inc/, /templates/, /components/, /print.cfm. No login/cookies/registration/PLZ check, ≥1 s per host.
Kept = heat-up dishes/soups (adapter meal filter); Fruchtaufstrich, Sirup, Kuchen, Apfelmus, Sugo/Bolognese, Klare
Rindssuppe (broth) and Pakete excluded with reason. biohof.at publishes no nutrition and no GTIN → never estimated.
Photos: official 'Haus-g'mocht' dish photos (marked 'Symbolfoto' by the shop) — vision-gated by the Daten-Squad.
Usage: python3 scripts/enrich_biohof_achleitner.py --cache DIR [--stamp YYYY-MM-DDTHHMM]"""
import sys, os, json, csv, time, datetime, argparse, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import biohof_achleitner as B
from food_connectors.http import UA, get

CSV = "data/online_mealprep.csv"
OPERATOR = {
    "name": "Achleitner Biohof GmbH", "seat": "Unterm Regenbogen 1, 4070 Eferding (AT)",
    "register": "FN 154057f (Landesgericht Wels)", "vat": "ATU41942706", "lei": "529900GY1B6OGAMV9D95",
    "management": "Andreas Achleitner (Geschäftsführung lt. Impressum und Firmenbuch)",
    "source": "https://www.biohof.at/impressum",
}
SHIPPING = {"source": "https://www.biohof.at/versandkosten + https://www.biohof.at/registrieren",
            "fee": "Biokiste (Mindestbestellwert 23 €) frei Haus; ohne Biokiste-Abo ab 30 € frachtfrei, darunter 4,50 €; Pfandkiste 10 € Anfangspfand",
            "area": "Oberösterreich, Salzburg, Steiermark, westliches Niederösterreich sowie einige Gebiete entlang der deutschen Grenze (Liefertag je PLZ)",
            "delivers_linz": True, "delivers_linz_basis": "Linz liegt in Oberösterreich = angegebenes Liefergebiet; PLZ-Prüfung (Registrierung) nicht aufgerufen"}
VISION = {
    "rule": "official biohof.at product photo for that artikelID, shows a plated dish of the named kind with the 'Haus-g'mocht' sticker; shop marks all as 'Symbolfoto' (serving suggestion, not a packshot)",
    "pass": ["2213", "2560", "3045", "3180", "3444", "4633", "4754", "4755", "4756", "4757", "4758", "4759", "2338"],
    "weak": {"2338": "Putenragout mit Schwammerl: Symbolfoto shows a creamy orange sauce/soup with parsley; turkey/mushrooms not clearly visible — kept as the shop's own photo for this article, flagged"},
}

def head(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA}), timeout=25) as r:
            return r.status
    except Exception as e:
        return getattr(e, "code", None) or repr(e)[:60]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache"); ap.add_argument("--stamp"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    cf = os.path.join(a.cache, "category.html") if a.cache else None
    cat = open(cf, encoding="utf-8").read() if cf and os.path.exists(cf) else get(B.CATEGORY, raw=True, timeout=40).decode("utf-8", "replace")
    tiles = B.parse_category(cat)
    kept, excluded = [], []
    for t in tiles:
        if not B.is_meal_name(t["name"]):
            excluded.append({"id": t["id"], "name": t["name"], "price_eur": t["price_eur"],
                             "reason": "Paket/Bundle" if "paket" in t["name"].lower() else "kein Fertiggericht (Aufstrich/Sirup/Kuchen/Apfelmus/Sauce/Brühe/Lax)"}); continue
        f = os.path.join(a.cache, t["id"] + ".html") if a.cache else None
        h = open(f, encoding="utf-8").read() if f and os.path.exists(f) else (time.sleep(1.0) or get(t["url"], raw=True, timeout=40).decode("utf-8", "replace"))
        p = B.parse_product(h, t["url"], t)
        d = p.to_dict(); d["extra"]["image_head"] = head(p.image_url); time.sleep(0.3)
        d["extra"]["vision_gate"] = "PASS" + (" (weak: " + VISION["weak"][p.source_id] + ")" if p.source_id in VISION["weak"] else "") if p.source_id in VISION["pass"] else "not checked"
        if d["extra"]["image_head"] != 200 or not d["extra"]["vision_gate"].startswith("PASS"):
            d["image_url"] = None
        kept.append(d)
    out = {"source": "biohof.at/hausgmocht-speisen + product pages (food-connectors biohof-achleitner adapter)", "fetched": stamp,
           "robots": "User-agent: * Allow: / — Disallow only /inc/ /templates/ /components/ /print.cfm (BLEXBot fully disallowed)",
           "operator": OPERATOR, "shipping_at": SHIPPING, "vision_gate": VISION, "category_tiles": len(tiles), "kept": len(kept),
           "with_nutrition": 0, "excluded": excluded, "products": kept}
    json.dump(out, open(f"raw/biohof_achleitner_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    day = stamp[:10]; rows = []
    for d in kept:
        x, size, price = d["extra"], d["size_g"], d["price_eur"]
        rows.append({"name": d["name"], "brand": "Biohof Achleitner", "store": B.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": round(price / size * 1000, 2) if size and price else None, "url": d["source_url"], "image_url": d["image_url"],
            "manufacturer": "Achleitner Biohof GmbH (Bio-Kulinarium Achleitner), Unterm Regenbogen 1, 4070 Eferding, FN 154057f",
            "origin": "AT (Eferding, OÖ)", "bio": bool(x.get("bio")), "veg": "vegan" if x.get("vegan") else None,
            "prep": f"{x['preparation']} (lt. biohof.at)" if x.get("preparation") else None, "category": "Online Meal-Prep",
            "price_source": f"biohof.at Produktseite Preis je Stück/Glas inkl. MwSt. {day} (Lieferung mit der Biokiste)", "price_date": day,
            "nut_source": None, "packaging": "Mehrweg-Glas" if x.get("mehrweg") else None, "online": True,
            "available": bool(x.get("orderable_this_week")), "storage": None,
            "shelf_life": None,
            "shipping_eur": 4.5, "nut_flag": "keine Nährwertangabe auf biohof.at (nicht geschätzt)" + (f"; Menge: {x['size_note']}" if x.get("size_note") else ""),
            "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != B.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    print("tiles", len(tiles), "kept", len(kept), "photos", sum(bool(d["image_url"]) for d in kept), "excluded", len(excluded), "csv rows", len(cur) + len(rows))

if __name__ == "__main__":
    main()
