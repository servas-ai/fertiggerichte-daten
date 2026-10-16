"""myProduct (myproduct.at) — Fertiggerichte regionaler Produzenten → evidence snapshot raw/myproduct_<stamp>.json
+ rows 'Online: myProduct' in data/online_mealprep.csv (idempotent replace) (Daten-Squad 2026-10-16T2111).

Source: food-connectors `myproduct` adapter — category https://myproduct.at/lebensmittel/fertiggerichte?p=N
(page dataLayer + tile links) → product pages (schema.org JSON-LD Offer + Magento attribute table: EAN,
Nettofüllmenge, Herstellerangaben, Zutaten, Allergene, Lagerhinweis, MHD, Produkteigenschaft, Nährwerte
je 100 g when published). robots.txt (*) disallows only Magento system paths, /catalogsearch/, /checkout/,
/customer/ and sorted/filtered list URLs. No login/cookies, ≥1 s per worker.
Pages may be read from a local crawl cache (--cache DIR) made with the same polite crawl.
Kept = finished dishes/soups with price, size and a HEAD-200 packshot; fonds, gravies, sauces/Bolognese,
spreads, dry mixes and spice sachets are excluded with a reason. Nutrition is never estimated: products whose
page says 'gesetzlich keine Nährwertkennzeichnung notwendig' keep empty nutrition + nut_flag.
Usage: python3 scripts/enrich_myproduct.py [--cache DIR] [--stamp YYYY-MM-DDTHHMM]"""
import sys, os, json, csv, time, datetime, argparse, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import myproduct as M
from food_connectors.http import UA

CSV = "data/online_mealprep.csv"
OPERATOR = {
    "name": "myProduct GmbH", "seat": "Karl Kastner-Straße 1, 3910 Zwettl (AT)", "office": "Industriestraße 2, 3300 Amstetten",
    "register": "FN 431059k (Landesgericht Krems)", "vat": "ATU69436808",
    "management": "Rainer Neuwirth M.A., KommR Christof Kastner, Mag. Herwig Gruber (Geschäftsführung lt. Impressum)",
    "founding_date_site": "2015-03-11 (schema.org Organization foundingDate on myproduct.at)",
    "vies": {"valid": True, "name": "myProduct GmbH", "address": "Karl Kastner-Straße 1, AT-3910 Zwettl-NÖ", "checked": "2026-10-16T21:20:55Z"},
    "gleif": None, "source": "https://myproduct.at/impressum + https://myproduct.at/agb",
}
SHIPPING = {"source": "https://myproduct.at/lieferung", "fee": "7,90 € je 10 kg Gesamtgewicht (inkl. Warenverpackung) innerhalb Österreichs",
            "dispatch": "1–2 Werktage (nur gekennzeichnete Artikel) bzw. 2–5 Werktage; Zustellung in Österreich i. d. R. innerhalb 24 h",
            "other_countries": "EU/CH über separaten Deutschland-Store"}


def head(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA}), timeout=25) as r:
            return r.status
    except Exception as e:
        return getattr(e, "code", None) or repr(e)[:60]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cache"); ap.add_argument("--stamp"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    if a.cache and os.path.exists(os.path.join(a.cache, "urls.json")):
        urls = json.load(open(os.path.join(a.cache, "urls.json")))
    else:
        urls = [i["url"] for i in M.category_items() if i.get("url")]
    kept, excluded, failed = [], [], []
    for u in urls:
        f = os.path.join(a.cache, "pages", os.path.basename(u) + ".html") if a.cache else None
        try:
            if f and os.path.exists(f) and os.path.getsize(f) > 1000:
                h = open(f, encoding="utf-8", errors="replace").read()
            else:
                time.sleep(1.0); h = M._html_get(u)
            p = M.parse_product(h, u)
        except Exception as e:
            failed.append({"url": u, "error": repr(e)[:120]}); continue
        d = p.to_dict()
        if not p.name:
            failed.append({"url": u, "error": "no JSON-LD Product"}); continue
        if not M.is_ready_meal(p):
            excluded.append({"url": u, "name": p.name, "sku": p.source_id, "reason": p.extra.get("exclusion") or "missing price/size/image"}); continue
        kept.append(d)
    for d in kept:
        d["extra"]["image_head"] = head(d["image_url"]); time.sleep(0.2)
    good = [d for d in kept if d["extra"]["image_head"] == 200]
    for d in kept:
        if d["extra"]["image_head"] != 200:
            excluded.append({"url": d["source_url"], "name": d["name"], "sku": d["source_id"], "reason": f"packshot HEAD {d['extra']['image_head']}"})
    out = {"source": "myproduct.at/lebensmittel/fertiggerichte + product pages (food-connectors myproduct adapter)", "fetched": stamp,
           "robots": "User-agent: * — Disallow only Magento system dirs, /catalogsearch/, /checkout/, /customer/, /wishlist/, sorted/filtered list params; category ?p=N and product pages allowed",
           "operator": OPERATOR, "shipping_at": SHIPPING, "category_items": len(urls), "kept": len(good),
           "with_nutrition": sum(bool(d["nutrition_100g"].get("protein") is not None) for d in good),
           "excluded": excluded, "failed": failed, "products": good}
    path = f"raw/myproduct_{stamp}.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    day = f"{stamp[:10]}"
    rows = []
    for d in good:
        n, x, size, price = d["nutrition_100g"], d["extra"], d["size_g"], d["price_eur"]
        pp = round(n["protein"] * size / 100, 1) if n.get("protein") is not None else None
        pc, us = x.get("pack_count") or 1, x.get("unit_size_g")
        rows.append({"name": d["name"], "brand": d["brand"], "store": M.STORE, "price_eur": price, "size_g": size,
            "price_per_kg": d["unit_price_eur"], "url": d["source_url"], "image_url": d["image_url"],
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None else None,
            "eur_per_10g_protein": round(price / pp * 10, 2) if pp else None, "nutriscore": None,
            "manufacturer": d["producer"], "producer_id": None, "origin": d["origin"], "bio": x.get("bio") or False,
            "veg": "vegan" if x.get("vegan") else None, "prep": None, "instantpot": None, "category": "Online Meal-Prep",
            "price_source": f"myproduct.at Produktseite (schema.org Offer, inkl. MwSt.) {day}", "price_date": day,
            "nut_source": f"myproduct.at Nährwertangaben je 100 g {day}" if n else None, "packaging": None, "online": True,
            "available": (x.get("availability") or "").lower() == "instock", "storage": x.get("storage"), "shelf_life": f"MHD {x['best_before']} (lt. Produktseite)" if x.get("best_before") else None,
            "shipping_eur": 7.90,
            "nut_flag": None if n else ("keine Nährwertangabe – lt. Produktseite gesetzlich nicht erforderlich (nicht geschätzt)" if "keine" in (x.get("nutrition_label") or "") else "keine Nährwertangabe auf der Produktseite (nicht geschätzt)"),
            "ean": d["ean"], "portions": f"{pc} × {us:g} g" if pc > 1 and us else None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8")))
    cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    print(path, "items", len(urls), "kept", len(good), "nutrition", out["with_nutrition"], "excluded", len(excluded), "failed", len(failed), "csv rows", len(cur) + len(rows))


if __name__ == "__main__":
    main()
