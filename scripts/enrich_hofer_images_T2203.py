"""Daten-Squad T2203: Hofer/Lidl/Penny photo tail via Open Food Facts by EXACT EAN only.

Candidates = photo-less Hofer/Lidl/Penny rows whose EAN is known (ean column or OFF product URL).
OFF product API (images + selected front) was queried for all 38; every image that exists was
downloaded and visually reviewed (T2203 vision gate). Only images that show the front of the very
same pack (brand + product name + size legible) are accepted; the accepted list is hard-coded below
with the reviewer's verdict, everything else is recorded as rejected with reason. Each accepted URL
is HEAD-checked (200, image/*) at run time before the row is patched. No name/similarity matching.
"""
import csv, json, os, sys, time, urllib.request
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = "2026-10-16T2203"
UA = "servas-ai-fertiggerichte-daten/1.0 (martin@servas.ai)"
ACCEPT = [  # product_id, ean, OFF image (400 px), verdict
    ("5d889e2bc42f", "4099200051932", "https://images.openfoodfacts.org/images/products/409/920/005/1932/front_hu.8.400.jpg",
     "selected front: GOOD Choice 'Chicken Burger' 2 db / 300 g tray (HU-labelled ALDI/Hofer pack, same EAN) = row Good Choice Burger Chicken 300 g"),
    ("58574e016ce1", "4099200146263", "https://images.openfoodfacts.org/images/products/409/920/014/6263/1.400.jpg",
     "raw image 1 = front sleeve 'GOOD Choice Schwammerlsauce mit Serviettenknödeln' = row Good Choice Schwammerlsauce 380 g"),
    ("7c66f883349e", "4099200043012", "https://images.openfoodfacts.org/images/products/409/920/004/3012/1.400.jpg",
     "raw image 1 = pack label 'Original Greisinger Berner Würstel 400 g' (Hofer) = row Original Greisinger Bernerwürstel 400 g"),
]
REJECT = {
    "4061461184797": "front_en is a photo of the unpacked baked pizza, not the packshot",
    "4061461307639": "only image 2 = back label/nutrition table",
    "4099200209906": "images 1+2 = lid ingredient/nutrition label, not a front packshot",
}

def head(u):
    req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.headers.get("Content-Type", "")

def main():
    probe = json.load(open("/tmp/t2203_off.json")) if os.path.exists("/tmp/t2203_off.json") else []
    acc = []
    for pid, ean, url, why in ACCEPT:
        st, ct = head(url)
        if st == 200 and ct.startswith("image/"):
            acc.append(dict(product_id=pid, ean=ean, image_url=url, off_product=f"https://world.openfoodfacts.org/product/{ean}",
                            head_status=st, content_type=ct, vision_verdict=why))
        time.sleep(0.5)
    by = {a["product_id"]: a["image_url"] for a in acc}
    # products.json (typed) + products.csv (text) patched in place, image_url only, only if still empty
    pj = json.load(open(f"{R}/data/products.json"))
    n = 0
    for x in pj:
        if x["product_id"] in by and not x.get("image_url"):
            x["image_url"] = by[x["product_id"]]; n += 1
    json.dump(pj, open(f"{R}/data/products.json", "w"), ensure_ascii=False, indent=1)
    rows = list(csv.DictReader(open(f"{R}/data/products.csv", newline="")))
    for x in rows:
        if x["product_id"] in by and not x["image_url"]:
            x["image_url"] = by[x["product_id"]]
    with open(f"{R}/data/products.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    ev = dict(run=RUN, fetched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              method="OFF product API by exact EAN (api/v2/product/<ean>.json, fields images/image_front_url); vision gate on every existing image; HEAD 200",
              candidates=len(probe), off_probe=probe, accepted=acc,
              rejected=[dict(ean=k, reason=v) for k, v in REJECT.items()],
              no_image_on_off="all other candidate EANs (12 Lidl, 5 Penny, 18 Hofer) have zero uploaded images on OFF",
              dead_ends=["hofer.at Akamai 403 (not bypassed)", "wokostswas.at robots Disallow /img/items",
                         "OFF search API brand pools HTTP 503 (rate limit/outage) except 'cucina' — no exact-EAN or exact name+size match",
                         "penny.at sitemap has no product pages"],
              patched_rows=n)
    json.dump(ev, open(f"{R}/raw/hofer_images_{RUN}.json", "w"), ensure_ascii=False, indent=1)
    print("accepted", len(acc), "patched", n)

if __name__ == "__main__":
    main()
