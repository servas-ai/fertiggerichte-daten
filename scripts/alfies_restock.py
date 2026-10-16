"""Alfies daytime restock pass (Daten-Squad 2026-10-14T0809).

Re-probes the public search-only Algolia index for all 5 Alfies warehouses (Wien altha/guthe/macu/grill, Graz graz;
'grill' = Wien Simmering/Favoriten/Schwechat per the shop's own POST /api/get-warehouse), takes the ids that the
previous raw excluded as 'out of stock in all AT warehouses' and that are now in stock in >=1 warehouse, fetches their
public catalogue detail (1 req/s) and applies exactly the T0740 gates (ready-meal category/title, price, kcal+protein
per 100 g, Atwater plausibility, HEAD-200 photo). Writes a new raw file = previous kept + newly kept, previous
excluded minus newly kept (+ refreshed reason/timestamp for the still-OOS ones), with a `restock` audit section.
Usage: PYTHONPATH=/workspace/food-connectors python3 scripts/alfies_restock.py raw/alfies_<prev>.json raw/alfies_<new>.json <stamp>
"""
import sys, json, time, datetime, urllib.request
from food_connectors.adapters import alfies as a
from food_connectors.http import UA

prev_path, out_path, stamp = sys.argv[1], sys.argv[2], sys.argv[3]
raw = json.load(open(prev_path))
WHS = ["altha", "guthe", "macu", "grill", "graz"]
WIEN = {"altha", "guthe", "macu", "grill"}
hits, st = {}, {}
for wh in WHS:
    for h in a.meal_hits(wh):
        hits.setdefault(str(h["id"]), {})[wh] = h
        st.setdefault(str(h["id"]), {})[wh] = bool((((h.get("whs") or {}).get(wh) or {}).get("availability") or {}).get("hasAvailableStock"))
    time.sleep(0.5)
kept_ids = {p["source_id"] for p in raw["kept"]}
oos = [e for e in raw["excluded"] if e.get("id") and e["reason"].startswith("out of stock")]
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def head(url):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except Exception as ex:
        return getattr(ex, "code", None) or str(ex)[:60]

new_kept, still, audit = [], [], []
for e in oos:
    s = st.get(e["id"]) or {}
    if not any(s.values()):
        e2 = dict(e); e2["reason"] = "out of stock in all AT warehouses at fetch time"; e2["rechecked"] = now; e2["stock_by_warehouse"] = s
        still.append(e2); continue
    wh_in = [w for w in WHS if s.get(w)]
    base_wh = "altha"  # price basis = Wien altha display price, as T0740
    hit = (hits[e["id"]].get(base_wh) or hits[e["id"]][wh_in[0]])
    time.sleep(1.0)
    try:
        det = a.detail(e["id"])
    except Exception as ex:
        det = None
    p = a.to_product(hit, det, base_wh)
    d = p.to_dict() if hasattr(p, "to_dict") else dict(p.__dict__)
    n = p.nutrition_100g or {}
    reason = None
    if not p.price_eur: reason = "no price"
    elif n.get("kcal") is None or n.get("protein") is None: reason = "no nutrition per 100 g published"
    elif not a.consistent(n): reason = "nutrition fails Atwater plausibility (e.g. kJ/kcal swapped)"
    hd = head(p.image_url) if p.image_url else None
    if not reason and hd != 200: reason = f"photo HEAD {hd}"
    d.setdefault("fetched_at", now)
    x = d["extra"]
    x["stock_by_warehouse"] = s
    x["available_wien"] = any(s.get(w) for w in WIEN)
    x["available_graz"] = bool(s.get("graz"))
    x["available_any"] = True
    gz = (((hits[e["id"]].get("graz") or {}).get("whs") or {}).get("graz") or {}).get("displayPrice") or {}
    x["price_graz_eur"] = gz.get("priceInclTax")
    x["image_head"] = hd
    x["restocked"] = {"previous_reason": e["reason"], "previous_fetch": raw["fetched"], "rechecked": now, "in_stock_at": wh_in}
    audit.append({"id": e["id"], "name": p.name, "in_stock_at": wh_in, "result": reason or "kept",
                  "kcal": n.get("kcal"), "protein": n.get("protein"), "price_eur": p.price_eur, "image_head": hd})
    if reason:
        still.append({"name": p.name, "id": e["id"], "reason": reason, "price_eur": p.price_eur,
                      "nutrition": n, "nutrition_raw": x.get("nutrition_raw"), "rechecked": now})
    else:
        new_kept.append(d)

other_ex = [e for e in raw["excluded"] if not (e.get("id") and e["reason"].startswith("out of stock"))]
raw2 = dict(raw)
raw2["fetched"] = stamp
raw2["kept"] = raw["kept"] + new_kept
raw2["excluded"] = other_ex + still
raw2["counts"] = dict(raw["counts"], kept=len(raw2["kept"]), excluded=len(raw2["excluded"]),
                      photos_head_200=sum(1 for k in raw2["kept"] if (k["extra"].get("image_head") == 200)),
                      with_pack_size=sum(1 for k in raw2["kept"] if k.get("size_g")))
raw2["restock"] = {"run": stamp, "rechecked": now, "warehouses_probed": WHS,
                   "warehouse_note": "grill = Wien (Simmering/Favoriten/Schwechat) via POST www.alfies.at/api/get-warehouse",
                   "meal_ids_in_index": len(st), "previous_oos": len(oos), "now_in_stock": len(audit),
                   "newly_kept": len(new_kept), "still_oos_everywhere": sum(1 for e in still if e["reason"].startswith("out of stock")),
                   "previously_kept_now_oos_everywhere": sum(1 for i in kept_ids if not any((st.get(i) or {}).values())),
                   "new_ids_not_seen_before": sorted(i for i in st if i not in kept_ids and i not in {e.get('id') for e in raw['excluded']}),
                   "items": audit}
json.dump(raw2, open(out_path, "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in raw2["restock"].items() if k != "items"}, ensure_ascii=False))
for it in audit: print(it)
