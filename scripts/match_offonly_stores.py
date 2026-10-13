"""Match Open-Food-Facts-only ready-meal rows (no store, no price) against live AT store connectors by EXACT GTIN.

Sources (all via servas-ai/food-connectors adapters, public endpoints, robots respected, no login/cookies):
  - Gurkerl.at   : search-metadata (brand+name) -> /api/v1/products/{id}/composition -> ean
  - MPreis shop  : robots-allowed product sitemap slug match -> product JSON-LD gtin
  - dm.at        : product sitemap slug match -> products.dm.de product JSON gtin
A row is mapped only when the store GTIN == the OFF barcode (leading zeros ignored). BILLA/SPAR/PENNY expose no
GTIN in their public JSON, so they are not used (no name-only guessing). Rows whose barcode already exists as a
store row in the dataset are reported as duplicates.
Usage: python3 match_offonly_stores.py IN.json OUT_EVIDENCE.json OUT_OVERLAY.json
"""
import json, re, sys, time, unicodedata, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters import mpreis_shop, dm_shop
from food_connectors.http import get

STOP = {"und", "mit", "der", "die", "das", "in", "a", "la", "le", "von", "fur", "fuer", "art", "nach", "aus", "tk", "bio", "port", "g"}
def norm(s):
    s = (s or "").lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()
def toks(s): return [t for t in norm(s).split() if len(t) >= 3 and t not in STOP and not t.isdigit()]
def same(a, b): return a and b and str(a).lstrip("0") == str(b).lstrip("0")
def slug_cands(urls, row, k=3):
    bt = toks(row.get("brand")); nt = toks(row.get("name"))
    if not nt: return []
    sc = []
    for u in urls:
        s = norm(u.rsplit("/", 1)[-1])
        if bt and not any(t in s for t in bt): continue
        hit = sum(t in s for t in nt) / len(nt)
        if hit >= 0.6: sc.append((hit, u))
    return [u for _, u in sorted(sc, reverse=True)[:k]]

rows = json.load(open(sys.argv[1]))
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
g = Gurkerl()
mp_urls = mpreis_shop.sitemap_urls(max_age_h=24 * 7)
dm_urls = dm_shop.sitemap_urls(max_age_h=24 * 7)
ev, ov = [], {}
for i, r in enumerate(rows):
    e = r.get("ean"); rec = {"ean": e, "name": r["name"], "brand": r.get("brand"), "checked": [], "match": None}
    if not e: ev.append(rec); continue
    q = " ".join(x for x in [r.get("brand") or "", r["name"]] if x)
    # Gurkerl
    try:
        res = g.search(q[:80], 10); time.sleep(0.4)
        nt = toks(r["name"])
        res = [p for p in res if nt and sum(t in norm(p.name) for t in nt) / len(nt) >= 0.5][:3]
        for p in res:
            p = g.enrich(p); time.sleep(0.4)
            rec["checked"].append({"store": "Gurkerl.at", "name": p.name, "ean": p.ean})
            if same(p.ean, e):
                rec["match"] = {"store": "Gurkerl.at", "name": p.name, "brand": p.brand, "price_eur": p.price_eur, "size_g": p.size_g,
                                "url": p.source_url, "image_url": p.image_url, "store_ean": p.ean, "method": "gtin-exact"}; break
    except Exception as ex: rec["checked"].append({"store": "Gurkerl.at", "error": str(ex)[:120]})
    # MPreis
    if not rec["match"]:
        for u in slug_cands(mp_urls, r):
            try:
                p = mpreis_shop.product(u); time.sleep(0.5)
            except Exception as ex: rec["checked"].append({"store": "MPreis", "url": u, "error": str(ex)[:80]}); continue
            if not p: continue
            rec["checked"].append({"store": "MPreis", "name": p.name, "ean": p.ean})
            if same(p.ean, e):
                rec["match"] = {"store": "MPreis", "name": p.name, "brand": p.brand, "price_eur": p.price_eur, "size_g": p.size_g,
                                "url": p.source_url or u, "image_url": p.image_url, "store_ean": p.ean, "method": "gtin-exact"}; break
    # dm
    if not rec["match"]:
        for u in slug_cands(dm_urls, r):
            m = re.search(r"/p/d/(\d+)/", u)
            try:
                p = dm_shop.product(int(m.group(1)), u); time.sleep(0.5)
            except Exception as ex: rec["checked"].append({"store": "dm", "url": u, "error": str(ex)[:80]}); continue
            rec["checked"].append({"store": "dm", "name": p.name, "ean": p.ean})
            if same(p.ean, e):
                rec["match"] = {"store": "dm", "name": p.name, "brand": p.brand, "price_eur": p.price_eur, "size_g": p.size_g,
                                "url": u, "image_url": p.image_url, "store_ean": p.ean, "method": "gtin-exact"}; break
    if rec["match"]:
        mm = dict(rec["match"]); mm["fetched_at"] = now; ov[str(e).lstrip("0")] = mm
    ev.append(rec)
    print(i, e, r["name"][:40], "->", rec["match"] and rec["match"]["store"], flush=True)
json.dump({"generated_at": now, "rows": len(rows), "matched": len(ov), "evidence": ev}, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
json.dump({"generated_at": now, "method": "exact GTIN = OFF barcode (Gurkerl composition / MPreis JSON-LD / dm product JSON)", "articles": ov},
          open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
print("matched", len(ov), "of", len(rows))
