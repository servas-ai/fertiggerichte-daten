"""Daten-Squad T2304 (2026-10-17): refresh the 17 BILLA price rows that were not 'live 2026'
(5 'Preis 2025' + 12 with an empty status from older heisse-preise snapshots) against the public
shop.billa.at product-discovery JSON (food-connectors `billa`; same calls the web shop makes, no login/cookies).
Matching: article number from the row URL, else exact name + pack size via search, else exact-EAN search with a
single hit. Multi-buy promotions ('ab 2 Packungen') are never taken: price.standard is used instead.
Writes data/prices.{csv,json} in place, raw/billa_reprice_2026-10-17T2304.json and an app patch
scripts/billa_reprice_T2304/app_price_patch.json (for the fertig export once the uid freeze lifts)."""
import json, csv, time, os, urllib.parse
from food_connectors.http import get
R = "/workspace/fertiggerichte-daten"; DAY = "2026-10-17"
# product_id -> (sku, how matched)
MAP = {
 "304804baaa16": ("00-687225", "article no. from row URL"),
 "3963fe22725e": ("00-2558", "exact name + 400 g via search (row URL article no. 002558 = 00-2558)"),
 "3a5a7ce405ed": ("00-11369", "exact name + 800 g via search; row URL points to 00-2154 = 400 g variant (conflict noted, pack size + old price match 800 g)"),
 "a254eb94a709": ("00-570454", "article no. from row URL"),
 "9ea01933b209": ("00-352300", "article no. from row URL"),
 "196dd1fda1cc": ("00-745583", "article no. from row URL"),
 "62fb42a65ba4": ("00-727864", "article no. from row URL"),
 "61eb6df6f83f": ("00-745596", "article no. from row URL"),
 "7a09a982158c": ("00-724508", "article no. from row URL"),
 "870d1c79be9c": ("00-392364", "article no. from row URL"),
 "fd306cd5c292": ("00-700821", "article no. from row URL"),
 "83809d233798": ("00-281768", "article no. from row URL"),
 "d839d4629ade": ("00-257781", "article no. from row URL"),
 "5997a4a4a76a": ("00-19687", "exact name + 1000 g via search (row URL article no. 0019687 = 00-19687)"),
 "36b19349359a": ("00-595811", "exact-EAN search 9010437013901, single hit 'BILLA Thunfischsalat Toskana Art' 160 g = row"),
 "d142be122c0a": ("00-736499", "exact-EAN search 9010437028196, single hit 'Clever Buchstabensuppe' = row brand Clever"),
}
NOT_FOUND = {"c9be2b4c468b": "Simply good Rigatoni caprese (EAN 9010437028486): EAN search 0 hits, name search no match -> not on shop.billa.at today, price left as is"}

def main():
    ev, patch = [], []
    for pid, (sku, how) in MAP.items():
        d = get(f"https://shop.billa.at/api/product-discovery/products/{sku}"); time.sleep(1.1)
        pr = d.get("price") or {}; reg = pr.get("regular") or {}; std = pr.get("standard") or {}
        multi = bool(reg.get("promotionText")) and reg.get("promotionType") == "FROM"
        use = std if (multi or not reg.get("value")) else reg
        price = use["value"] / 100; ppu = (use.get("perStandardizedQuantity") or 0) / 100 or None
        unit, fac = pr.get("baseUnitShort"), float(pr.get("basePriceFactor") or 1)
        ppk = round(ppu * (1000 / fac), 2) if (ppu and unit == "g") else (ppu if unit == "kg" else None)
        rec = {"product_id": pid, "sku": sku, "matched_by": how, "api_name": d.get("name"), "brand": (d.get("brand") or {}).get("name"),
               "amount": f"{d.get('amount')} {d.get('volumeLabelShort')}", "price_eur": price, "price_per_kg_eur": ppk,
               "regular_raw": reg, "standard_raw": std, "multi_buy_skipped": multi, "published": d.get("published"),
               "url": f"https://shop.billa.at/produkte/{d.get('slug')}", "fetched_at": DAY}
        ev.append(rec)
        patch.append({"product_id": pid, "price": price, "ppk": ppk, "pstat": "live 2026",
                      "psrc": f"shop.billa.at product-discovery API {DAY} (food-connectors billa, {sku})"})
    by = {p["product_id"]: p for p in patch}
    for fn in ("prices.json",):
        rows = json.load(open(f"{R}/data/{fn}"))
        for x in rows:
            p = by.get(x["product_id"])
            if p and x["chain"] == "Billa":
                x.update(price_eur=p["price"], price_per_kg_eur=p["ppk"], price_status="live 2026", fetched_at=DAY, price_source=p["psrc"])
        json.dump(rows, open(f"{R}/data/{fn}", "w"), ensure_ascii=False, indent=1)
    rows = list(csv.DictReader(open(f"{R}/data/prices.csv"))); fields = list(rows[0])
    for x in rows:
        p = by.get(x["product_id"])
        if p and x["chain"] == "Billa":
            x.update(price_eur=p["price"], price_per_kg_eur=p["ppk"] if p["ppk"] is not None else "", price_status="live 2026", fetched_at=DAY, price_source=p["psrc"])
    with open(f"{R}/data/prices.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fields); w.writeheader(); w.writerows(rows)
    os.makedirs(f"{R}/scripts/billa_reprice_T2304", exist_ok=True)
    json.dump(patch, open(f"{R}/scripts/billa_reprice_T2304/app_price_patch.json", "w"), ensure_ascii=False, indent=1)
    json.dump({"run": "Daten-Squad 2026-10-17T2304", "source": "https://shop.billa.at/api/product-discovery/products/<sku>",
               "robots": "shop.billa.at public JSON used by the web shop; no login, cookies or cart; polite ~1 req/s",
               "updated": ev, "not_found": NOT_FOUND}, open(f"{R}/raw/billa_reprice_2026-10-17T2304.json", "w"), ensure_ascii=False, indent=1)
    for r in ev: print(r["product_id"], r["sku"], r["api_name"], r["amount"], r["price_eur"], r["price_per_kg_eur"], "MULTI-SKIPPED" if r["multi_buy_skipped"] else "")
if __name__ == "__main__": main()
