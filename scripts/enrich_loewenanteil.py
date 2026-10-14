"""Löwenanteil (loewenanteil.com) Bio glass-jar ready meals → evidence snapshot raw/loewenanteil_<stamp>.json
(Daten-Squad 2026-10-14T0441).

Source: food-connectors `loewenanteil` adapter — public Shopify storefront JSON
www.loewenanteil.com/products.json (price EUR, SKU, availability, images) + public product HTML
(Nährwerte pro 100 g + pro Glas, Zutaten, Zubereitung). robots.txt (*) Disallow includes /policies/
/cart /account /checkouts — product pages + products.json allowed; shipping/legal-notice NOT fetched.
No login/cookies, 1 req/s. Ready meals = product_type Fertiggericht, tag single, jar grams ≥800,
not mm_pasta. AT delivery evidenced by homepage country selector 'Österreich (EUR €)' (fee under
robots-Disallow /policies/shipping-policy → shipping_eur null). Every image URL is HEAD-checked;
candidates without a published nutrition table are listed in `dropped`.
Usage: python3 scripts/enrich_loewenanteil.py [--products-json FILE]"""
import sys, json, time, datetime, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import loewenanteil as L
from food_connectors.http import UA

def main(products_json=None, stamp=None):
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    shop = L.shop_products(); time.sleep(1.0)
    cand = [p for p in shop if L.is_meal(p)]
    if products_json:
        prods = json.load(open(products_json))["products"]
    else:
        prods = [p.to_dict() for p in L.Loewenanteil().fetch()]
    got = {p["extra"]["handle"] for p in prods}
    dropped = [{"handle": c["handle"], "title": c["title"], "sku": (c.get("variants") or [{}])[0].get("sku"),
                "reason": "no published Nährwerte table / size / protein on product page (nulls not invented)"}
               for c in cand if c["handle"] not in got]
    keep = []
    for p in prods:
        try:
            with urllib.request.urlopen(urllib.request.Request(p["image_url"], method="HEAD", headers={"User-Agent": UA}), timeout=20) as r:
                p["extra"]["image_head"] = r.status
        except Exception as e:
            p["extra"]["image_head"] = getattr(e, "code", None) or repr(e)[:60]
        time.sleep(0.3); keep.append(p)
    out = {
        "source": "www.loewenanteil.com/products.json + product HTML (food-connectors loewenanteil adapter)",
        "fetched": stamp,
        "robots": "User-agent: * Disallow: /policies/ /cart /account /checkouts /orders /admin /search … (product pages + /products.json allowed; /policies/shipping-policy and /policies/legal-notice NOT fetched)",
        "operator": {
            "name": "Löwenanteil GmbH",
            "seat": "Heiligengeiststraße 6–8, 26121 Oldenburg (DE)",
            "register": "HRB 212808 (AG Oldenburg)",
            "vat": "DE316057151",
            "source": "North Data / online-handelsregister.de public extract (footer © Löwenanteil GmbH on homepage; /policies/legal-notice robots-Disallow)",
        },
        "shipping_at": {
            "evidence": "https://www.loewenanteil.com/ homepage country selector lists 'Österreich (EUR €)'",
            "fee": None,
            "fee_note": "/policies/shipping-policy is robots-Disallow — not scraped; independent reviews mention ~6,99 € / free from 79 € but not used as primary source",
        },
        "shop_products": len(shop), "meal_candidates": len(cand), "kept": len(keep), "dropped": dropped, "products": keep,
    }
    path = f"raw/loewenanteil_{stamp}.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "kept", len(keep), "dropped", len(dropped),
          "img200", sum(p["extra"]["image_head"] == 200 for p in keep))
    return path

if __name__ == "__main__":
    pj = sys.argv[sys.argv.index("--products-json") + 1] if "--products-json" in sys.argv else None
    main(pj, "2026-10-14T0441" if not pj else None)
