"""bofrost* Austria (bofrost.at) ready meals → evidence snapshot raw/bofrost_<stamp>.json (Daten-Squad 2026-10-14T0238).

Source: food-connectors `bofrost` adapter — public product sitemap + product pages (schema.org JSON-LD price,
availability, images; pack line with €/kg; nutrition per 100 g; ingredients; Nutri-Score badge). robots.txt (*) only
disallows /cart /checkout /account /shop/ajax/ /crm — not used. No login/cookies, 1 request/s.
Only finished dishes (adapter is_meal_url + is_ready_meal): no ice/desserts/sides/plain Knödel/Spätzle/Suppeneinlagen.
Every image URL is HEAD-checked; rows without price, pack size or nutrition are skipped (none on 2026-10-14).
Usage: python3 scripts/enrich_bofrost.py [--html-cache DIR]   (cache = previously fetched pages, else live)"""
import sys, json, time, os, datetime, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import bofrost as B
from food_connectors.http import get, UA

def main(cache=None, stamp=None, product_xml=None):
    stamp = stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M")
    urls = B.product_urls(product_xml=product_xml); meal = [u for u in urls if B.is_meal_url(u)]
    keep, dropped = [], []
    for u in meal:
        no = B.article_no(u); f = os.path.join(cache, no + ".html") if cache else None
        if f and os.path.exists(f): h = open(f, encoding="utf-8").read()
        else: h = get(u, raw=True, timeout=40).decode("utf-8", "replace"); time.sleep(1.0)
        p = B.parse_product(h, u)
        if not B.is_ready_meal(p): dropped.append({"article": no, "name": p.name, "category": p.category, "reason": "not a finished dish"}); continue
        if not (p.price_eur and p.size_g and p.nutrition_100g.get("protein") is not None):
            dropped.append({"article": no, "name": p.name, "reason": "missing price/size/nutrition"}); continue
        try:
            with urllib.request.urlopen(urllib.request.Request(p.image_url, method="HEAD", headers={"User-Agent": UA}), timeout=20) as r:
                p.extra["image_head"] = r.status
        except Exception as e: p.extra["image_head"] = getattr(e, "code", None) or repr(e)[:60]
        time.sleep(0.3)
        keep.append(p.to_dict())
    out = {"source": "bofrost.at public sitemap + product pages (food-connectors bofrost adapter)", "fetched": stamp,
           "robots": "User-agent: * Disallow: /cart /checkout /account /shop/ajax/ /crm (none used)",
           "operator": {"name": "bofrost* Austria GmbH", "seat": "6430 Ötztal-Bahnhof (Tirol)", "fn": "FN 185873v (LG Innsbruck)",
                        "uid": "ATU66058936", "source": "https://www.bofrost.at/impressum.html"},
           "niederlassung_ooe": "bofrost* Sattledt, Welser Str. 3, 4642 Sattledt (https://www.bofrost.at/niederlassungen.html)",
           "sitemap_products": len(urls), "meal_candidates": len(meal), "kept": len(keep), "dropped": dropped, "products": keep}
    path = f"raw/bofrost_{stamp}.json"; json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)
    print(path, "kept", len(keep), "dropped", len(dropped)); return path

if __name__ == "__main__":
    c = sys.argv[sys.argv.index("--html-cache") + 1] if "--html-cache" in sys.argv else None
    x = open(sys.argv[sys.argv.index("--sitemap") + 1]).read() if "--sitemap" in sys.argv else None
    main(c, "2026-10-14T0238" if c else None, x)
