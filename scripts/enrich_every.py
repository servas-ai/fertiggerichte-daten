"""every. (every-foods.com) frozen ready meals → evidence snapshot raw/every_<stamp>.json (Daten-Squad 2026-10-14T0341).

Source: food-connectors `every` adapter — public Shopify storefront JSON eat.every-foods.com/products.json (price EUR,
SKU, availability, images) + public product pages every-foods.com/products/<handle> (Storyblok product blok: weight,
nutrition per 100 g + per pack, ingredients, preparation). robots.txt (*) disallows only /account/ /api/ /discount/ — not
used. No login/cookies, 1 request/s. Ready meals = product_type "Meal", price > 0, listed in the DE product sitemap.
AT delivery verified on the shop's own shipping policy (eat.every-foods.com/policies/shipping-policy: "Österreich (DPD)").
Every image URL is HEAD-checked; candidates without a product blok / weight / nutrition are listed in `dropped`.
Usage: python3 scripts/enrich_every.py [--products-json FILE]   (FILE = adapter output {"fetched","products"}; else live)"""
import sys, json, re, time, datetime, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import every as E
from food_connectors.http import UA

def main(products_json=None, stamp=None):
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    shop = E.shop_products(); time.sleep(1.0); handles = E.sitemap_handles()
    cand = [p for p in shop if E.is_meal(p, handles)]
    if products_json:
        prods = json.load(open(products_json))["products"]
    else:
        prods = [p.to_dict() for p in E.Every().fetch()]
    got = {p["extra"]["handle"] for p in prods}
    dropped = [{"handle": c["handle"], "title": c["title"], "sku": c["variants"][0].get("sku"),
                "reason": "no product blok / weight / nutrition table published on every-foods.com product page (nulls not invented)"}
               for c in cand if c["handle"] not in got]
    keep = []
    for p in prods:
        try:
            with urllib.request.urlopen(urllib.request.Request(p["image_url"], method="HEAD", headers={"User-Agent": UA}), timeout=20) as r:
                p["extra"]["image_head"] = r.status
        except Exception as e: p["extra"]["image_head"] = getattr(e, "code", None) or repr(e)[:60]
        time.sleep(0.3); keep.append(p)
    out = {"source": "eat.every-foods.com/products.json + every-foods.com product pages (food-connectors every adapter)", "fetched": stamp,
           "robots": "User-Agent: * Allow: / Disallow: /account/ /api/ /discount/ (none used)",
           "operator": {"name": "Every. GmbH", "seat": "Ritterstraße 9–10, 10969 Berlin (DE)", "register": "HRB 221768 B (AG Charlottenburg)",
                        "vat": "DE335586517", "bio_control": "DE-ÖKO-001 (Kiwa BCS)", "source": "https://every-foods.com/impressum"},
           "shipping_at": {"evidence": "https://eat.every-foods.com/policies/shipping-policy",
                           "quote": "Österreich (DPD) … Wir liefern Dein Paket zu Deinem Wunschdatum innerhalb 24 Stunden in Deutschland, Österreich, Dänemark, Niederlande, Belgien und Luxemburg.",
                           "fee": "Der reguläre Versand kostet € 5,99, ab einer Bestellung von 8 Gerichten ist der Versand frei. Express … € 7,99",
                           "conflict": "AGB §6(1) (eat.every-foods.com/policies/terms-of-service) still says 'nur … Adressen in Deutschland'"},
           "shop_products": len(shop), "meal_candidates": len(cand), "kept": len(keep), "dropped": dropped, "products": keep}
    path = f"raw/every_{stamp}.json"; json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "kept", len(keep), "dropped", len(dropped), "img200", sum(p["extra"]["image_head"] == 200 for p in keep)); return path

if __name__ == "__main__":
    pj = sys.argv[sys.argv.index("--products-json") + 1] if "--products-json" in sys.argv else None
    main(pj, "2026-10-14T0341" if pj else None)
