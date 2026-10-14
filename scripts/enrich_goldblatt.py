"""Goldblatt (goldblatt.at) High Protein Bio glass-jar ready meals → evidence snapshot raw/goldblatt_<stamp>.json
(Daten-Squad 2026-10-14T0537).

Source: food-connectors `goldblatt` adapter — public Shopify storefront JSON
goldblatt.at/products.json (price EUR, SKU, availability, images) + public product HTML
(Nährwerte pro 100 g + pro Glas (500 g), Zutaten, Zubereitung). robots.txt (*) Allow: / —
product pages + products.json + /policies/shipping-policy + /policies/legal-notice allowed.
No login/cookies, 1 req/s. Ready meals = product_type High Protein Bio-Fertiggerichte, single
jars (not bundle/probier/monats), shipping grams ≥500. AT delivery published on shipping-policy
(5,99 € ab 30 € / gratis ab 90 €). Every image URL is HEAD-checked.
Usage: python3 scripts/enrich_goldblatt.py"""
import sys, json, time, datetime, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import goldblatt as G
from food_connectors.http import UA

def main(stamp=None):
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    shop = G.shop_products(); time.sleep(1.0)
    cand = [p for p in shop if G.is_meal(p)]
    prods = [p.to_dict() for p in G.Goldblatt().fetch()]
    got = {p["extra"]["handle"] for p in prods}
    dropped = [{"handle": c["handle"], "title": c["title"], "sku": (c.get("variants") or [{}])[0].get("sku"),
                "reason": "no published Nährwerte table / size / protein on product page (nulls not invented)"}
               for c in cand if c["handle"] not in got]
    for p in prods:
        try:
            with urllib.request.urlopen(urllib.request.Request(p["image_url"], method="HEAD", headers={"User-Agent": UA}), timeout=20) as r:
                p["extra"]["image_head"] = r.status
        except Exception as e:
            p["extra"]["image_head"] = getattr(e, "code", None) or repr(e)[:60]
        time.sleep(0.3)
    out = {
        "source": "goldblatt.at/products.json + product HTML (food-connectors goldblatt adapter)",
        "fetched": stamp,
        "robots": "User-agent: * Allow: / (product pages + /products.json + /policies/ allowed; /admin /cart /checkout Disallow)",
        "operator": {
            "name": "Golden Veggies GmbH", "trading_as": "Goldblatt",
            "seat": "Wagerberg 37, 8271 Bad Waltersdorf (AT)",
            "register": "FN 550344f (Landesgericht Graz)", "vat": "ATU76525048",
            "management": "Matthias Wiesenhofer, MSc. (Geschäftsführer)",
            "vies": {"valid": True, "name": "Golden Veggies GmbH",
                     "address": "Wagerberg 37\nAT-8271 Bad Waltersdorf", "checked": "2026-10-14T05:41:28Z"},
            "gleif": None, "source": "https://goldblatt.at/policies/legal-notice",
        },
        "shipping_at": {
            "evidence": "https://goldblatt.at/policies/shipping-policy",
            "fee": 5.99, "fee_below_30": 9.99, "free_from": 90.0, "carrier": "Österreichische Post",
        },
        "shop_products": len(shop), "meal_candidates": len(cand), "kept": len(prods),
        "dropped": dropped, "products": prods,
    }
    path = f"raw/goldblatt_{stamp}.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "kept", len(prods), "dropped", len(dropped),
          "img200", sum(p["extra"]["image_head"] == 200 for p in prods))
    return path

if __name__ == "__main__":
    main("2026-10-14T0537")
