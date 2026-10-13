"""Enrich dm ready-meal rows that lack image_url (strict match only, never fabricate).

Sources, in access order (official JSON first):
  1. dm.at product sitemap (https://www.dm.at/product-sitemap.xml, robots-allowed) → DAN per product URL
  2. dm public product JSON https://products.dm.de/product/products/detail/AT/dan/{dan}
     (no login, no cookies; same JSON the dm.at product page renders). Non-AI images only.
     Match: row URL DAN == API DAN, or normalized "<brand> <title>" == row name (incl. pack size).
  3. Lotao official Shopify https://www.lotao.com/products.json — title + pack size must match.
  4. Open Food Facts product API by barcode (codes found via OFF search) — brand + name + quantity must match.
Every image URL is GET-verified (status 200, content-type image/*, >1 kB) before use.
dm.at /search is robots-disallowed → not used.

Writes raw/dm_images_YYYY-MM-DD.json (evidence), raw/dm_images_overlay.json and
/workspace/fertig/dm_images_overlay.json (consumed by fertig/score.py), and data/products.{csv,json}.
"""
from __future__ import annotations
import csv, json, os, re, sys, time, unicodedata, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA, RAW = os.path.join(ROOT, "data"), os.path.join(ROOT, "raw")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 ServasFoodResearch/1.0"
OFF_UA = "ServasFoodResearch/1.0 (fertig@servas.ai)"
DM_API = "https://products.dm.de/product/products/detail/AT/dan/{dan}"
READY = re.compile(r"little-lunch|lotao|tressbrueder|dmbio-(fertiggericht|eintopf|gulasch|chili|bowl)|fertiggericht|eintopf")
# OFF barcodes located via OFF search 2026-10-13 (verified again below against brand/name/quantity)
OFF_CODES = {"Little Lunch Fertiggericht Pilz Risotto, 350 g": "4260614721791",
             "dmBio Fertiggericht Linsen Dal mit Kartoffeln, 280 g": "4066447440881",
             "Lotao Fertiggericht Veggie Curry, 320 g": "4260237451099"}

def norm(s):
    s = unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", s.replace("&", "und"))

def get(url, ua=UA, raw=False, timeout=30):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json,*/*"}), timeout=timeout)
    b = r.read(); return (b, r.headers.get("content-type") or "") if raw else json.loads(b)

def verify(url):
    try:
        b, ct = get(url, raw=True)
        return ct.startswith("image/") and len(b) > 1000, ct, len(b)
    except Exception as e:
        return False, type(e).__name__, 0

def size_of(s):
    m = re.search(r"(\d+(?:,\d+)?)\s*(g|kg|ml)\b", s or "", re.I)
    if not m: return None
    v = float(m.group(1).replace(",", ".")); return v * 1000 if m.group(2).lower() == "kg" else v

def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prods = json.load(open(os.path.join(DATA, "products.json")))
    dm = [p for p in prods if (p.get("chain") or "").lower() == "dm"]
    todo = [p for p in dm if not (p.get("image_url") or "").strip()]
    print("dm rows", len(dm), "without photo", len(todo))
    sm = get("https://www.dm.at/product-sitemap.xml", raw=True)[0].decode()
    urls = sorted(set(u for u in re.findall(r"https://www\.dm\.at/p/d/\d+/[a-z0-9-]+", sm) if READY.search(u)))
    api = {}
    for u in urls:
        dan = int(re.search(r"/p/d/(\d+)/", u).group(1))
        try:
            d = get(DM_API.format(dan=dan))
            title = (d.get("title") or {}).get("headline") if isinstance(d.get("title"), dict) else d.get("title")
            imgs = [i["src"] for i in d.get("images") or [] if i.get("src") and not i.get("isAiGenerated")]
            api[dan] = dict(dan=dan, url=u, api=DM_API.format(dan=dan), gtin=d.get("gtin"), brand=(d.get("brand") or {}).get("name"),
                            title=title, price=(((d.get("price") or {}).get("price") or {}).get("current") or {}).get("value"), images=imgs)
        except Exception as e:
            api[dan] = dict(dan=dan, url=u, error=str(e)[:80])
        time.sleep(1.0)
    by_name = {norm(f"{v.get('brand')} {v.get('title')}"): v for v in api.values() if v.get("title")}
    lotao = get("https://www.lotao.com/products.json?limit=250")["products"]
    ev, overlay = [], []
    for p in todo:
        name, rec = p["name"], None
        m = re.search(r"/p/d/(\d+)/", p.get("url") or "")
        cand = api.get(int(m.group(1))) if m else by_name.get(norm(name))
        if cand and cand.get("images"):
            rec = dict(method="dm.at product JSON (DAN from sitemap)" + (" · URL DAN match" if m else " · exact brand+title+size match"),
                       image_url=cand["images"][0], dm_dan=cand["dan"], dm_url=cand["url"], gtin=cand.get("gtin"),
                       dm_title=f"{cand.get('brand')} {cand.get('title')}", dm_price_live=cand.get("price"))
        if not rec and norm(name).startswith("lotao"):
            for lp in lotao:
                t = norm("lotao " + lp["title"]); sizes = {size_of(v["title"]) for v in lp["variants"]}
                if t and t in norm(name.replace("Fertiggericht ", "")) and size_of(name) in sizes and lp.get("images"):
                    rec = dict(method="Lotao official Shopify products.json · title+pack size match", image_url=lp["images"][0]["src"],
                               source=f"https://www.lotao.com/products/{lp['handle']}", manufacturer_title=lp["title"]); break
        if not rec and name in OFF_CODES:
            c = OFF_CODES[name]
            try:
                o = get(f"https://world.openfoodfacts.org/api/v2/product/{c}?fields=code,product_name,brands,quantity,image_front_url", ua=OFF_UA).get("product") or {}
                ok = norm(o.get("product_name")) in norm(name) and norm((o.get("brands") or "").split(",")[0]) in norm(name) and size_of(o.get("quantity")) == size_of(name)
                if ok and o.get("image_front_url"):
                    rec = dict(method="Open Food Facts product API · brand+name+quantity match", image_url=o["image_front_url"],
                               source=f"https://world.openfoodfacts.org/product/{c}", gtin=c, off_name=o.get("product_name"), off_quantity=o.get("quantity"))
            except Exception as e:
                print("OFF fail", c, e)
            time.sleep(1.0)
        if rec:
            ok, ct, n = verify(rec["image_url"]); rec.update(verified=ok, content_type=ct, bytes=n); time.sleep(0.6)
            if not ok: rec = dict(rec, rejected="image GET verify failed")
        e = dict(product_id=p["product_id"], name=name, **(rec or {"unmatched": True}))
        ev.append(e)
        if rec and rec.get("verified"):
            p["image_url"] = rec["image_url"]; overlay.append(dict(name=name, image_url=rec["image_url"], method=rec["method"]))
    day = now[:10]
    json.dump(dict(fetched_at=now, sources=["https://www.dm.at/product-sitemap.xml", "https://products.dm.de/product/products/detail/AT/dan/{dan}",
                   "https://www.lotao.com/products.json", "https://world.openfoodfacts.org/api/v2/product/{code}"],
                   dm_rows=len(dm), without_photo_before=len(todo), filled=len(overlay), dm_api_products=list(api.values()), matches=ev),
              open(os.path.join(RAW, f"dm_images_{day}.json"), "w"), ensure_ascii=False, indent=1)
    ov = dict(fetched_at=now, method="dm.at product JSON / Lotao Shopify / OFF strict match, GET-verified", images=overlay)
    json.dump(ov, open(os.path.join(RAW, "dm_images_overlay.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(ov, open("/workspace/fertig/dm_images_overlay.json", "w"), ensure_ascii=False, indent=1)
    fields = list(prods[0].keys())
    with open(os.path.join(DATA, "products.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore"); w.writeheader()
        for r in prods: w.writerow({k: ("|".join(map(str, v)) if isinstance(v, list) else v) for k, v in r.items()})
    json.dump(prods, open(os.path.join(DATA, "products.json"), "w"), ensure_ascii=False, indent=1)
    have = sum(1 for p in dm if (p.get("image_url") or "").strip())
    print(f"filled {len(overlay)} · dm photos {len(dm)-len(todo)}→{have}/{len(dm)}")
    for e in ev:
        if not e.get("verified"): print("  open:", e["name"], e.get("rejected") or "")

if __name__ == "__main__":
    main()
