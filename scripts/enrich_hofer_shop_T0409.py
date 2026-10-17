"""Daten-Squad T0409 (2026-10-17): Hofer via the new live food-connectors `hofer-shop` adapter.
hofer.at public product sitemap (robots allow; /*?q= search disallowed and not used) + product pages (__NUXT_DATA__),
polite 1 req/s. Evidence: raw/hofer_shop_2026-10-17T0409.json (95 slug candidates crawled, 18 ready meals by filter).
  * +10 current Hofer heat-up meals (the same 10 rows the app imported in fertig 6d33a96 / fertig-app 6352364; product_id =
    export.py formula sha1(url|name|store)), price re-verified live, official packshots (Aldi Scene7 CDN) vision-gated.
    hofer.at publishes no nutrition/EAN → none (never estimated). Samyang XXL Buldak Instant Nudeln 650 g excluded (instant
    noodle multipack, same rule as the app); Pizz'Ah Picco Belli Flammkuchen has no price on hofer.at → not added.
  * 8 existing rows whose hofer.at SKU is in the sitemap: price re-confirmed live 2026-10-17 (fetched_at set).
  * e0767bfa4193 'Rindsgulasch (ca. 0,5 kg)' (Sonnhof, SKU 510738): page says '100% Rindfleisch', 'Rohes Fleisch' → raw diced
    beef, not a ready meal → removed. 594b376ca923 'Hot Dog' = same SKU 741950 as a0a23c8cd654 'Good Choice Hot Dog' → duplicate removed.
  * 212 Hofer rows not in the sitemap: price_source gets the app's note 'nicht mehr auf hofer.at gelistet (sitemap 2026-10-17)'.
Run: python3 scripts/enrich_hofer_shop_T0409.py [--write]"""
import csv, hashlib, json, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRAWL = os.environ.get("HOFER_CRAWL", "/tmp/hofer_crawl_keep.json")
APP = os.environ.get("FERTIG_APP", "/workspace/fertig-app/public") + "/data.json"
TODAY = "2026-10-17"; SLOT = "2026-10-17T0409"
REMOVE = {"e0767bfa4193": "raw diced beef (hofer.at: '100% Rindfleisch', 'Rohes Fleisch … vor dem Verzehr gut durcherhitzen'), not a ready meal",
          "594b376ca923": "duplicate of a0a23c8cd654 (same hofer.at SKU 000000000000741950)"}
STALE_NOTE = "nicht mehr auf hofer.at gelistet (sitemap_products.xml 2026-10-17) – evtl. ausgelistet"
pid = lambda r: hashlib.sha1(((r.get("url") or "") + "|" + r["name"] + "|" + r["store"]).encode()).hexdigest()[:12]
sku = lambda u: (re.search(r"-(\d{18})/?$", u or "") or [None, None])[1]

crawl = json.load(open(CRAWL)); live = {r["source_id"]: r for r in crawl["rows"] if "source_id" in r}
app = [r for r in json.load(open(APP))["rows"] if r.get("store") == "Hofer"]
def load(n): return json.load(open(f"{R}/data/{n}.json"))
P, PR, N = load("products"), load("prices"), load("nutrition")
have = {p["product_id"] for p in P}
new_p, new_pr, confirmed, stale_marked, rejected = [], [], [], 0, []
for r in app:
    i = pid(r); s = sku(r.get("url")); lv = live.get(s)
    if "sitemap" in (r.get("psrc") or "") and i not in have:
        if not lv or lv.get("price_eur") != r.get("price") or not lv.get("image_url"):
            rejected.append({"name": r["name"], "reason": "live re-check mismatch/no image"}); continue
        new_p.append({"product_id": i, "name": r["name"], "brand": r.get("brand"), "chain": "Hofer", "dish": r.get("dish"),
            "storage": r.get("pack"), "pack_size_g": lv.get("size_g") or r.get("size"), "producer": None, "origin": None,
            "bio": r.get("bio"), "vegan": r.get("vegan"), "url": r["url"], "image_url": lv["image_url"],
            "source": f"hofer.at Produktseite via food-connectors hofer-shop ({TODAY})", "ean": None})
        x = lv["extra"]
        new_pr.append({"product_id": i, "chain": "Hofer", "price_eur": lv["price_eur"], "price_per_kg_eur": lv.get("unit_price_eur"),
            "price_status": "live 2026", "fetched_at": TODAY,
            "price_source": f"food-connectors hofer-shop {TODAY} (hofer.at Produktseite __NUXT_DATA__, sitemap_products.xml): Regalpreis {lv['price_eur']} €; {x.get('comparison_display') or ''}; {x.get('on_sale_display') or ''}".replace("\xa0", " ")})
byid = {p["product_id"]: p for p in P}
for x in PR:
    p = byid.get(x["product_id"])
    if not p or p["chain"] != "Hofer" or x["product_id"] in REMOVE: continue
    s = sku(p.get("url"))
    if s in live and live[s].get("price_eur") == x["price_eur"]:
        x["fetched_at"] = TODAY
        if "hofer-shop" not in (x["price_source"] or ""):
            x["price_source"] = f"{x['price_source']}; bestätigt live {TODAY} via food-connectors hofer-shop (hofer.at Produktseite)"
        confirmed.append(p["name"])
stale_ids = {pid(r) for r in app if r.get("price_stale") and "nicht mehr auf hofer.at" in (r.get("price_note") or "")}
for x in PR:
    if x["product_id"] in stale_ids and STALE_NOTE not in (x["price_source"] or ""):
        x["price_source"] = f"{x['price_source'] or ''} – {STALE_NOTE}".strip(" –"); stale_marked += 1
removed = [p for p in P if p["product_id"] in REMOVE]
P = [p for p in P if p["product_id"] not in REMOVE] + new_p
PR = [x for x in PR if x["product_id"] not in REMOVE] + new_pr
N = [x for x in N if x["product_id"] not in REMOVE]
print({"new": len(new_p), "confirmed": len(confirmed), "stale_marked": stale_marked, "removed": [p["name"] for p in removed], "rejected": rejected})
if "--write" in sys.argv:
    for n, rows in (("products", P), ("prices", PR), ("nutrition", N)):
        json.dump(rows, open(f"{R}/data/{n}.json", "w"), ensure_ascii=False, indent=1)
        fields = list(csv.DictReader(open(f"{R}/data/{n}.csv")).fieldnames)
        with open(f"{R}/data/{n}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fields, extrasaction="ignore"); w.writeheader()
            for r in rows: w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
        sp = f"{R}/data/supplemental/{n}.json"
        if os.path.exists(sp):
            sj = [r for r in json.load(open(sp)) if r["product_id"] not in REMOVE]
            ids = {r["product_id"] for r in sj}
            sj += [r for r in {"products": new_p, "prices": new_pr, "nutrition": []}[n] if r["product_id"] not in ids]
            json.dump(sj, open(sp, "w"), ensure_ascii=False, indent=1)
    ev = {"slot": SLOT, "connector": "food-connectors hofer-shop (new)", "robots": "hofer.at robots.txt 2026-10-17: User-agent * Disallow /tools, /*?q= only",
          "sitemap_n": crawl["sitemap_n"], "candidates_crawled": crawl["candidates"],
          "ready_meals_by_filter": [r["name"] for r in crawl["rows"] if r.get("is_ready_meal")],
          "added": new_p, "added_prices": new_pr, "confirmed_live": confirmed, "stale_marked": stale_marked,
          "removed": [{**p, "reason": REMOVE[p["product_id"]]} for p in removed], "rejected": rejected,
          "not_added": {"Samyang XXL Buldak Instant Nudeln, Carbonara 650 g": "instant noodle multipack (app meal filter)",
                        "Pizz'Ah Picco Belli, Flammkuchen 360 g": "no price on hofer.at product page"},
          "vision_gate": "10/10 packshots = official front-of-pack images of the named SKU (contact sheet checked 2026-10-17T04:2x)",
          "crawl_rows": crawl["rows"]}
    json.dump(ev, open(f"{R}/raw/hofer_shop_{SLOT}.json", "w"), ensure_ascii=False, indent=1)
