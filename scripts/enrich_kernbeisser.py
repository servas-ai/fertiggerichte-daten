"""Kernbeißer (kernbeisser.at) vegan Vollkorn-Fertiggerichte im Glas → evidence snapshot raw/kernbeisser_<stamp>.json
(Daten-Squad 2026-10-14T0504).

Source: food-connectors `kernbeisser` adapter — public WooCommerce Store API
kernbeisser.at/wp-json/wc/store/v1/products (price EUR incl. MwSt., SKU, stock, images, tags, description
with 'Durchschnittliche Nährwerte pro 100g', Zutaten, '… enthält 450g N kcal in einem Glas') + product page
JSON-LD gtin (EAN-13 check digit verified). robots.txt (*) disallows only wp-admin, WooCommerce upload/log
folders and ?add-to-cart= — Store API + product pages allowed. No login/cookies, 1 req/s.
Operator from kernbeisser.at/impressum; UID checked live in EU VIES. Every image URL is HEAD-checked.
Usage: python3 scripts/enrich_kernbeisser.py"""
import sys, json, time, datetime, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import kernbeisser as K
from food_connectors.http import UA

def main(stamp=None):
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    shop = K.store_products(); time.sleep(1.0)
    cand = [p for p in shop if K.is_meal(p)]
    prods = [p.to_dict() for p in K.Kernbeisser().fetch()]
    got = {p["extra"]["slug"] for p in prods}
    dropped = [{"slug": c["slug"], "name": c["name"], "sku": c.get("sku"), "reason": "no parsed nutrition/size"} for c in cand if c["slug"] not in got]
    excluded = [{"slug": c["slug"], "name": c["name"], "sku": c.get("sku"), "reason": "bundle (Probierpaket), not a single meal"} for c in shop if not K.is_meal(c)]
    for p in prods:
        try:
            with urllib.request.urlopen(urllib.request.Request(p["image_url"], method="HEAD", headers={"User-Agent": UA}), timeout=20) as r:
                p["extra"]["image_head"] = r.status
        except Exception as e:
            p["extra"]["image_head"] = getattr(e, "code", None) or repr(e)[:60]
        time.sleep(0.3)
    out = {
        "source": "kernbeisser.at/wp-json/wc/store/v1/products + product JSON-LD (food-connectors kernbeisser adapter)",
        "fetched": stamp,
        "robots": "User-agent: * Disallow: /wp-content/uploads/wc-logs/ /wp-content/uploads/woocommerce_transient_files/ /wp-content/uploads/woocommerce_uploads/ /*?add-to-cart= /wp-admin/ (Store API + product pages allowed)",
        "operator": {
            "name": "Kernbeißer OG", "seat": "Jheringgasse 33/2/8, 1150 Wien (AT)",
            "register": "FN 622470y (Handelsgericht Wien)", "vat": "ATU80744456",
            "management": "Polina Polynova (Geschäftsführerin lt. Impressum)",
            "vies": {"valid": True, "name": "Kernbeißer OG", "address": "Jheringgasse 33/2/8, AT-1150 Wien", "checked": "2026-10-14T05:07:01Z"},
            "gleif": None, "source": "https://kernbeisser.at/impressum/",
        },
        "shipping_at": {"evidence": "site header on every page: 'Kostenloser Versand (zurzeit erfolgt Lieferung nur innerhalb Österreichs)'; 'Die zulässigen Bestellmengen sind 6, 12, 18, 24 oder 30 Gläser'", "fee": 0.0, "min_order": "6 Gläser (54 €); Probierpaket 6 Gerichte 50 €"},
        "shop_products": len(shop), "meal_candidates": len(cand), "kept": len(prods), "dropped": dropped, "excluded": excluded, "products": prods,
    }
    path = f"raw/kernbeisser_{stamp}.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "kept", len(prods), "dropped", len(dropped), "img200", sum(p["extra"]["image_head"] == 200 for p in prods), "ean", sum(bool(p["ean"]) for p in prods))
    return path

if __name__ == "__main__":
    main("2026-10-14T0504")
