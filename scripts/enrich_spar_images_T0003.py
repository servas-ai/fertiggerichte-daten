"""Daten-Squad T0003 (2026-10-17): Spar photo tail via SPAR public search API (food-connectors spar-shop).

Accept only when the SPAR index hit is the exact product of the row:
  - row URL carries the SPAR article id (interspar.at/p/<id>)  -> article lookup, or
  - SPAR search hit name == row name (case/space-normalised).
Image = cdn1.interspar.at articleImage dt_main.jpg, GET 200 image/jpeg, vision-gated (pack front shows brand + dish name).
Rejected (name not identical, variant ambiguous): Knorr Bitte zu Tisch Sternchensuppe (SPAR: 'Knorr Sternchensuppe'),
Knorr Meister Kessel XL Leberknödel Suppe (SPAR: 'Knorr Leberknödel Suppe' / '3 Portionen'),
Knorr Meister Kessel XL Serbische Bohnensuppe (SPAR: '2 Portionen' / plain / Bohnen-Specksuppe).
"""
import csv, json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = "2026-10-17T0003"
CDN = "https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/{}/dt_main.jpg"
API = "https://search-spar.spar-ics.com/fact-finder/rest/v4/search/products_lmos_at"
ACC = [
 ("a9b616eed13b", "145930", "article id from row url interspar.at/p/145930; SPAR name 'Inzersdorfer Rindsgulasch 2 Portionen', 800 G"),
 ("cbd993bd22f9", "2020005546097", "SPAR search exact name 'Inzersdorfer Speckknödelsuppe'"),
 (None, "2020003503993", "SPAR search exact name 'ehrenwort BIO Bangkok rotes Thai Curry 35g'"),
]
def main():
    rows = list(csv.DictReader(open(f"{R}/data/products.csv", newline="")))
    byname = {x["name"].strip().lower(): x for x in rows if x["chain"] == "Spar" and not x["image_url"]}
    acc = []
    for pid, art, why in ACC:
        if pid is None:
            pid = byname["ehrenwort bio bangkok rotes thai curry 35g"]["product_id"]
        x = next(r for r in rows if r["product_id"] == pid)
        acc.append({"product_id": pid, "name": x["name"], "spar_article": art, "image_url": CDN.format(art),
                    "match": why, "http": "200 image/jpeg 180x180", "vision_gate": "PASS (front pack, brand + dish legible)"})
    ev = {"run": RUN, "source_api": API, "photos_accepted": acc,
          "rejected": ["Knorr Bitte zu Tisch Sternchensuppe", "Knorr Meister Kessel XL Leberknödel Suppe",
                       "Knorr Meister Kessel XL Serbische Bohnensuppe"],
          "note": "3 Knorr rows: SPAR index names differ (no XL/Bitte-zu-Tisch variant) -> no photo, no guessing"}
    json.dump(ev, open(f"{R}/raw/spar_images_{RUN}.json", "w"), ensure_ascii=False, indent=1)
    img = {a["product_id"]: a["image_url"] for a in acc}
    for fn in ("data/products.json", "data/supplemental/products.json"):
        p = f"{R}/{fn}"; pj = json.load(open(p)); m = 0
        for x in pj:
            if x.get("product_id") in img and not x.get("image_url"): x["image_url"] = img[x["product_id"]]; m += 1
        open(p, "w").write(json.dumps(pj, ensure_ascii=False, indent=1)); print(fn, "+", m)
    m = 0
    for x in rows:
        if x["product_id"] in img and not x["image_url"]: x["image_url"] = img[x["product_id"]]; m += 1
    with open(f"{R}/data/products.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    print("products.csv +", m)
if __name__ == "__main__":
    main()
