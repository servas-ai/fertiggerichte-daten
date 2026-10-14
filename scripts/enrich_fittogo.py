"""fit2go.meals (fittogo.at) ready meals → evidence snapshot raw/fittogo_<stamp>.json (Daten-Squad 2026-10-14T0307).

Source: food-connectors `fittogo` adapter — public product sitemap + product HTML pages
(Gesamt-Einwaage, pack nutrition kcal/Protein/Carbs/Fett, packshot). Hydrogen shop:
/products.json returns 404; robots allow product pages + sitemap. No login/cookies, 1 req/s.
price_eur = published 12er-box meal price (9,99 €); individual SKU shows 0,00 €.
Every image URL is HEAD-checked. Usage: python3 scripts/enrich_fittogo.py"""
import sys, json, time, os, datetime, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import fittogo as F
from food_connectors.http import get, UA

def main(stamp=None):
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    urls = F.product_urls()
    keep, dropped = [], []
    for u in urls:
        try:
            h = get(u, raw=True, timeout=40).decode("utf-8", "replace")
        except Exception as e:
            dropped.append({"url": u, "reason": f"fetch {e!r}"}); time.sleep(1.0); continue
        p = F.parse_product(h, u)
        if not F.is_ready_meal(p):
            dropped.append({"url": u, "name": p.name, "reason": "not a ready meal / missing size or nutrition"})
            time.sleep(1.0); continue
        try:
            with urllib.request.urlopen(urllib.request.Request(p.image_url, method="HEAD", headers={"User-Agent": UA}), timeout=20) as r:
                p.extra["image_head"] = r.status
        except Exception as e:
            p.extra["image_head"] = getattr(e, "code", None) or repr(e)[:60]
        time.sleep(0.3)
        keep.append(p.to_dict()); time.sleep(0.7)
    out = {
        "source": "fittogo.at public product sitemap + product HTML (food-connectors fittogo adapter)",
        "fetched": stamp,
        "robots": "User-agent: * Disallow: /cart /account /collections/*sort_by* /search/?* (product pages + sitemap allowed; /products.json 404 on Hydrogen)",
        "operator": {"name": "Fit2go GmbH", "seat": "Piccoloweg 4, 4055 Pucking (OÖ)", "fn": "FN 615822x",
                     "uid": "ATU80022878", "source": "https://fittogo.at/pages/impressum"},
        "shipping": "4,99 € österreichweit Express (Di–Do Versand) lt. fittogo.at",
        "price_policy": F.BOX_PRICE_NOTE,
        "sitemap_meals": len(urls), "kept": len(keep), "dropped": dropped, "products": keep,
    }
    path = f"raw/fittogo_{stamp}.json"
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "kept", len(keep), "dropped", len(dropped)); return path

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
