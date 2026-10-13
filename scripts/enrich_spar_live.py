"""SPAR ready meals: live 2026 prices from SPAR's public product search API (never fabricated).

Source: food-connectors `spar-shop` adapter → https://search-spar.spar-ics.com/fact-finder/rest/v4/search/products_lmos_at
(the JSON index the interspar.at shop queries; no robots.txt on that host, no login/cookies; interspar.at HTML/Cloudflare
is never requested). Lookup is exact by SPAR article number taken from the row's interspar.at/p/<id> URL.

Writes:
  raw/spar_live_<stamp>.json            evidence (every probed article + decision)
  /workspace/fertig/spar_live_overlay.json  {article_id: live price fields} — applied in score.py BEFORE price_status
Rows whose article number returns no hit are NOT changed (kept as flagged Altpreis rows, listed as not_listed).
Usage: python3 enrich_spar_live.py [--all]   (default: only Spar rows that are not 'live 2026')
"""
from __future__ import annotations
import json, os, re, sys, time
from datetime import datetime, timezone
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters.spar_shop import article, API, SparShop  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FERTIG = "/workspace/fertig"
AID = re.compile(r"/p/(\d{4,})|articleImage\.dam/at/(\d{4,})/")
norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower().replace("ß", "ss").replace("’", "").replace("'", ""))

def main():
    now = datetime.now(timezone.utc); stamp, day = now.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y-%m-%d")
    items = json.load(open(os.path.join(FERTIG, "scored.json")))
    items = items if isinstance(items, list) else items.get("items") or items.get("products")
    spar = [x for x in items if "spar" in (x.get("store") or "").lower()]
    todo = spar if "--all" in sys.argv else [x for x in spar if x.get("price_status") != "live 2026"]
    path = os.path.join(FERTIG, "spar_live_overlay.json")
    ov = json.load(open(path)) if os.path.exists(path) else {"source": API, "articles": {}}
    probed, seen = [], set()
    for x in todo:
        m = AID.search(x.get("url") or "") or AID.search(x.get("image_url") or "")
        aid = (m.group(1) or m.group(2)) if m else None
        if not aid:
            # no article number: exact normalized name match (brand + SPAR name) in the search index, else skip
            try: hits = SparShop().search(x.get("name") or "", 10)
            except Exception: hits = []
            time.sleep(0.4)
            ex = [h for h in hits if norm(h.name) == norm(x.get("name"))]
            if len(ex) != 1:
                probed.append(dict(name=x.get("name"), decision=f"skip: no article number and {len(ex)} exact name hits")); continue
            aid = ex[0].source_id
        if aid in seen: continue
        seen.add(aid)
        try: p = article(aid)
        except Exception as e:
            probed.append(dict(name=x.get("name"), article_id=aid, decision=f"error: {type(e).__name__}")); time.sleep(1); continue
        time.sleep(0.4)
        if not p:
            probed.append(dict(name=x.get("name"), article_id=aid, old_price=x.get("price_eur"), old_date=x.get("price_date"),
                               decision="not listed: article number has no hit in SPAR search index → unchanged")); continue
        if p.extra.get("item_type") == "WeightProduct":
            probed.append(dict(name=x.get("name"), article_id=aid, spar_name=p.name, stock_status=p.extra.get("stock_status"),
                               decision="skip: weight/counter product (price per 100 g) → listed, price unchanged")); continue
        if not p.price_eur:
            probed.append(dict(name=x.get("name"), article_id=aid, decision="skip: hit without price")); continue
        rec = dict(price_eur=p.price_eur, regular_price_eur=p.extra.get("regular_price_eur"), on_promotion=p.extra.get("on_promotion"),
                   price_per_unit=p.unit_price_eur, unit=p.unit, spar_code_internal=p.extra.get("spar_code_internal"), spar_name=p.name, pack=p.extra.get("pack"),
                   stock_status=p.extra.get("stock_status"), image_url=p.image_url, fetched_at=stamp,
                   price_source=f"SPAR Such-API live {day} (search-spar.spar-ics.com, Artikel {aid})")
        ov["articles"][aid] = rec
        probed.append(dict(name=x.get("name"), article_id=aid, old_price=x.get("price_eur"), old_date=x.get("price_date"),
                           old_status=x.get("price_status"), new_price=p.price_eur, spar_name=p.name, decision="live"))
    ov["updated_at"] = stamp
    json.dump(ov, open(path, "w"), ensure_ascii=False, indent=1)
    ev = dict(fetched_at=stamp, source=API, method="exact article-number lookup (articleNumberSearch), food-connectors spar-shop",
              rows_considered=len(todo), probed=probed,
              summary={k: sum(1 for p in probed if p["decision"].startswith(k)) for k in ("live", "not listed", "skip", "error")})
    json.dump(ev, open(os.path.join(ROOT, "raw", f"spar_live_{now.strftime('%Y-%m-%dT%H')}.json"), "w"), ensure_ascii=False, indent=1)
    print(ev["summary"], "changed price:", sum(1 for p in probed if p["decision"] == "live" and p["old_price"] != p["new_price"]))

if __name__ == "__main__":
    main()
