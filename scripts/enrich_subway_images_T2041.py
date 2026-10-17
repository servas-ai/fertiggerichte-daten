"""Daten-Squad T2041 (2026-10-17): Subway photo gap 0/59 -> official AT menu tile photos.

Source: subway.com/de-AT menu category pages (server-rendered; robots.txt '*' disallows only /sitecore/ and
non-AT deliverylocator paths): /Sandwiches, /SubMelts, /SubwaySeries ('Unsere Kreationen'). Each tile =
<div id="MenuCatProduct_<ProductId>"> + <img src=/de-at/ns/images/menu/AST/GER/...> + <h3> product name.
Product detail pages return 'Not found' from the box, so only category tiles are used.

Accept only when the tile name is the same product as the row (PDF menu name, case/punctuation-normalised):
  - 'Sub 15 cm' rows <- Sandwiches tiles (14), 'Panini' rows <- SubMelts tiles (3; 'Smokey Beast' on the AT
    site = 'Smoky Beast' in the AT nutrition PDF), 'Sub 15 cm (Kreation)' rows <- Unsere Kreationen (4).
  - Wrap (17) and Salat (17) rows: the site has only one generic 'Wraps' / 'Salate' tile -> not taken.
  - Not on the AT site today: Dölicious Chicken, Plant-based Dölicious Chicken, Smashed Falafel, The BBQ Master
    -> no photo (no guessing). Great Caesar / The Philly Boss tiles have no dataset row (not added here).
Each image GET 200 (image/png|jpeg, 234x140; Veggie Delite 594x334) and vision-gated on a contact sheet.
Seven Sandwiches tiles are the 'Sub des Tages' variants with a weekday badge (MONTAG..SONNTAG) - accepted,
noted. Kreation tiles show the sub at a longer length than the row's 15 cm - accepted as official dish photo, noted.
"""
import csv, json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = "2026-10-17T2041"
B = "https://www.subway.com/de-at/ns/images/menu/AST/GER/"
CAT = "https://www.subway.com/de-AT/MenuNutrition/Menu/"
# (row name, AT ProductId, AT tile name, category page, image file, note)
ACC = [
 ("Chicken Teriyaki (Sub 15 cm)", "5254", "Chicken Teriyaki", "Sandwiches", "Subway_Produktbilder_Subs_234x140_SUB_Chicken-Teriyaki.jpeg", ""),
 ("Plant-based Chicken Teriyaki (Sub 15 cm)", "9223", "Plant-based Chicken Teriyaki", "Sandwiches", "Plant_based_Chick_Teriy_SdT_234x140.png", "Sub des Tages badge MITTWOCH"),
 ("Chicken Fajita (Sub 15 cm)", "5253", "Chicken Fajita", "Sandwiches", "Chicken_Fajita_SdT_234x140.png", "Sub des Tages badge DONNERSTAG"),
 ("Rotisserie-Style Chicken (Sub 15 cm)", "12166", "Rotisserie-Style Chicken", "Sandwiches", "Produktbilder_15cm_Rotisserie_Style_Chicken_234x140.png", ""),
 ("Chicken Tandoori (Sub 15 cm)", "11878", "Chicken Tandoori", "Sandwiches", "Chicken_Tandoori_SdT_234x140.png", "Sub des Tages badge SAMSTAG"),
 ("Tuna (Sub 15 cm)", "5261", "Tuna", "Sandwiches", "Tuna_SdT_234x140.png", "Sub des Tages badge FREITAG"),
 ("Italian B.M.T. (Sub 15 cm)", "5257", "Italian B.M.T.®", "Sandwiches", "Italian_BMT_SdT_234x140.png", "Sub des Tages badge MONTAG"),
 ("BBQ Rib (Sub 15 cm)", "5250", "BBQ Rib", "Sandwiches", "BBQ_Rib_SdT_Product_thumbnails_234x140.png", "Sub des Tages badge SONNTAG"),
 ("Nacho Chicken (Sub 15 cm)", "12942", "Nacho Chicken", "Sandwiches", "Nacho_Chicken_SdT_234x140.png", "Sub des Tages badge DIENSTAG"),
 ("Philly Beef & Cheese (Sub 15 cm)", "5260", "Philly Beef & Cheese", "Sandwiches", "Subway_Produktbilder_Subs_234x140_Sub-Philly-Beef-Cheese.jpeg", ""),
 ("Salami (Sub 15 cm)", "5258", "Salami", "Sandwiches", "Produktbilder_Salami_234x140.png", ""),
 ("Ham (Sub 15 cm)", "5255", "Ham", "Sandwiches", "Produktbilder_Ham_234x140.png", ""),
 ("Spicy Vegan Patty (Sub 15 cm)", "7591", "Spicy Vegan Patty", "Sandwiches", "Produktbilder_Spicy_Vegan_Patty_234x140.png", ""),
 ("Veggie Delite (Sub 15 cm)", "5247", "Veggie Delite®", "Sandwiches", "594x334Veggie_Delite.jpg", "594x334"),
 ("Chick'n'Garlic (Panini)", "12593", "Chick 'N' Garlic", "SubMelts", "Produktbilder_Series-melt_234x140_ChicknGarlic.jpg", ""),
 ("Philly Supreme (Panini)", "12130", "Philly Supreme", "SubMelts", "Produktbilder_Series-melt_234x140_Philly-Supreme.jpg", ""),
 ("Smoky Beast (Panini)", "12124", "Smokey Beast", "SubMelts", "Produktbilder_Series-melt_234x140_Smokey-Beast.jpg", "AT site spells 'Smokey', PDF 'Smoky'"),
 ("Furious Chicken (Sub 15 cm (Kreation))", "12120", "Furious Chicken", "SubwaySeries", "Furious_Chicken_UnsKreat_234x140.png", "photo shows a longer sub than 15 cm"),
 ("Fiesta Fajita (Sub 15 cm (Kreation))", "12107", "Fiesta Fajita", "SubwaySeries", "Fiesta_Fajita_UnsKreat_234x140.png", "photo shows a longer sub than 15 cm"),
 ("Tasty Tandoori (Sub 15 cm (Kreation))", "13247", "Tasty Tandoori", "SubwaySeries", "Tasty_Tandoori_UnsKreat_234x140.png", "photo shows a longer sub than 15 cm"),
 ("Beef Texicana (Sub 15 cm (Kreation))", "13246", "Beef Texicana", "SubwaySeries", "Beef_Texicana_UnsKreat_234x140.png", "photo shows a longer sub than 15 cm"),
]
REJ = {
 "wrap_and_salad_rows": "34 rows (17 Wrap, 17 Salat): AT site shows only one generic 'Wraps' tile (ProductId 7083) and one generic 'Salate' tile (5249) -> not product-specific, not taken",
 "not_on_at_site": ["Dölicious Chicken (Sub 15 cm)", "Plant-based Dölicious Chicken (Sub 15 cm)", "Smashed Falafel (Sub 15 cm)", "The BBQ Master (Sub 15 cm (Kreation))"],
 "at_tiles_without_row": ["Great Caesar (12118)", "The Philly Boss (12116)", "Kids' Pak Ham/Veggie Delite/Salami", "Breakfast subs", "Nacho Chicken Bites", "Waffle Fries"],
}
def main():
    rows = list(csv.DictReader(open(f"{R}/data/products.csv", newline="")))
    sw = {x["name"]: x for x in rows if x["chain"] == "Subway"}
    acc = []
    for name, pid, tile, cat, f, note in ACC:
        x = sw[name]
        acc.append({"product_id": x["product_id"], "name": name, "at_product_id": pid, "at_tile_name": tile,
                    "category_page": CAT + cat, "image_url": B + f, "http": "GET 200",
                    "vision_gate": "PASS (sandwich/panini matches the named dish)" + (f"; {note}" if note else "")})
    ev = {"run": RUN, "source": "subway.com/de-AT menu category pages (server-rendered tiles)",
          "robots": "https://www.subway.com/robots.txt: '*' Disallow /sitecore/ + non-AT deliverylocator only",
          "photos_accepted": acc, "rejected": REJ}
    json.dump(ev, open(f"{R}/raw/subway_images_{RUN}.json", "w"), ensure_ascii=False, indent=1)
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
