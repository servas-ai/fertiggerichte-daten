"""Daten-Squad T2340 (2026-10-17): refresh the 34 SPAR price rows that were not 'live 2026'
(31 'Preis 2025' + 3 empty-status OFF-sourced rows) against SPAR's public product search API
(food-connectors `spar-shop`, search-spar.spar-ics.com fact-finder; no login/cookies; interspar.at Cloudflare HTML never requested).
Probe of all 34 (raw/spar_reprice_probe_2026-10-17T2340.json): exact article number from the row URL, else name search.
Only taken: piece products (item-type Product), in stock, same name (brand line) and same pack size / €/kg as the row.
Never taken: WeightProduct counter items (price per kg / 100 g, not per pack), pack-size mismatches, articles gone from the index.
SPAR code-internal is NOT a GTIN, so EAN rows were matched by exact name + pack; EAN search returns 0 hits on this index.
Writes data/prices.{csv,json}, raw/spar_reprice_2026-10-17T2340.json and scripts/spar_reprice_T2340/app_price_patch.json."""
import json, csv, time, os, sys
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import spar_shop as S
R = "/workspace/fertiggerichte-daten"; DAY = "2026-10-17"
MAP = {
 "938f807a366e": ("2020003995446", "name search: 'SPAR PREMIUM Ratatouille Gemüse-Eintopf Vegan' 400 g (row = 'SPAR PREMIUM Edition Johanna Maier …', same line; old price + €/kg 9,98 = 400 g)"),
 "833307a71a84": ("2020003995460", "name search: 'SPAR PREMIUM Süsskartoffel- Eintopf Vegan' 400 g (row = Johanna Maier edition; old €/kg 12,47 = 400 g)"),
 "26a676865192": ("2020005643550", "exact name search 'S-BUDGET Mini-Hühner-Schnitzel' 700 g (old €/kg 9,27 = 700 g)"),
 "0efddae4c91a": ("2020005857414", "name search: 'SPAR Natur*pur Bio-Tomaten-Risotto' 200 g; old price 2,49 + €/kg 12,45 identical; row EAN 4099200013428 not verifiable (SPAR code-internal is not a GTIN)"),
 "5aa873963beb": ("6426149", "name search: 'Iglo Backhendlstreifen Klassik' 250 g, old price 8,99 identical; row EAN 8722700143956 not verifiable on this index"),
 "2229d87a3a24": ("2020004633187", "name search: 'SPAR Feine Küche Paprika-Huhn mit Eierspätzle' 400 g, old price 4,99 identical; row EAN 9100000992167 = SPAR AT own-brand prefix"),
 "7c534dab449d": ("2020002311964", "name search: 'Inzersdorfer Kräftige Hühnersuppe' 400 g, old price 2,99 identical; row EAN 9002600645118"),
}
NOT_TAKEN = {
 "WeightProduct (counter/weight item, API price is per kg or per 100 g, not per pack)": ["1050c737afbf", "57c9ab798052", "9927e9b4dc2e", "2a7bd95a743d", "4ae4622fd27c", "622399661bcb", "4c5c1664ef35", "de56729e5912"],
 "pack-size mismatch (article 577052 is 700 g at 7,49 €, row is 350 g at 4,99 €; also outOfStock)": ["3a490fb14acf"],
 "article number no longer in SPAR's index (delisted, re-checked 2026-10-17)": ["04a13d204e17", "cc0f749998aa", "58970cc9f0a9", "bb3d95f44397", "af60759b9f29", "50750912a500", "062c59051a72", "e51f8dba71f3", "35111e7e8b73", "a4f2839087c2", "5e6e153b6076", "3f74c1a8b5e2", "48b51eb19d5b", "a52b60d2e451", "c553f0b91b72", "7075c99a8b56"],
 "no search hit": ["049e52ea3f12", "febef23813dd"],
}
def main():
    ev, patch = [], []
    for pid, (sku, how) in MAP.items():
        p = S.article(sku); time.sleep(1.1)
        assert p and p.extra.get("item_type") == "Product", (pid, sku)
        rec = {"product_id": pid, "spar_article": sku, "matched_by": how, "api_name": p.name, "pack": p.extra.get("pack"), "price_eur": p.price_eur,
               "price_per_kg_eur": p.unit_price_eur if p.unit == "kg" else None, "regular_price_eur": p.extra.get("regular_price_eur"),
               "on_promotion": p.extra.get("on_promotion"), "stock_status": p.extra.get("stock_status"), "url": p.source_url, "fetched_at": DAY}
        if rec["on_promotion"]:  # shelf promo is temporary: use the regular price
            rec["price_eur"] = rec["regular_price_eur"]
        ev.append(rec)
        patch.append({"product_id": pid, "price": rec["price_eur"], "ppk": rec["price_per_kg_eur"], "pstat": "live 2026",
                      "psrc": f"SPAR Such-API live {DAY} (search-spar.spar-ics.com, food-connectors spar-shop, {sku})"})
    by = {p["product_id"]: p for p in patch}
    rows = json.load(open(f"{R}/data/prices.json"))
    for x in rows:
        p = by.get(x["product_id"])
        if p and x["chain"] == "Spar":
            x.update(price_eur=p["price"], price_per_kg_eur=p["ppk"], price_status="live 2026", fetched_at=DAY, price_source=p["psrc"])
    json.dump(rows, open(f"{R}/data/prices.json", "w"), ensure_ascii=False, indent=1)
    rows = list(csv.DictReader(open(f"{R}/data/prices.csv"))); fields = list(rows[0])
    for x in rows:
        p = by.get(x["product_id"])
        if p and x["chain"] == "Spar":
            x.update(price_eur=p["price"], price_per_kg_eur=p["ppk"] if p["ppk"] is not None else "", price_status="live 2026", fetched_at=DAY, price_source=p["psrc"])
    with open(f"{R}/data/prices.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fields); w.writeheader(); w.writerows(rows)
    os.makedirs(f"{R}/scripts/spar_reprice_T2340", exist_ok=True)
    json.dump(patch, open(f"{R}/scripts/spar_reprice_T2340/app_price_patch.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"run": "Daten-Squad 2026-10-17T2340", "source": S.API, "probe": "raw/spar_reprice_probe_2026-10-17T2340.json",
               "robots": "search host has no robots.txt (404); no login/cookies; interspar.at HTML never requested; ~1 req/s",
               "updated": ev, "not_taken": NOT_TAKEN}, open(f"{R}/raw/spar_reprice_2026-10-17T2340.json", "w"), ensure_ascii=False, indent=1)
    for r in ev: print(r["product_id"], r["spar_article"], r["api_name"], r["pack"], r["price_eur"], r["price_per_kg_eur"], r["stock_status"], "PROMO" if r["on_promotion"] else "")
if __name__ == "__main__": main()
