"""Merge bofrost* Austria (bofrost.at) ready meals into online_mealprep.json — idempotent (replaces all 'Online: bofrost*' rows).
Source: newest evidence snapshot fertiggerichte-daten/raw/bofrost_<stamp>.json written by scripts/enrich_bofrost.py
(food-connectors `bofrost` adapter: public sitemap + product pages, JSON-LD price, pack line with €/kg, nutrition per 100 g,
Nutri-Score badge). Snapshot instead of a live crawl so the hourly export does not hit bofrost.at ~150 times.
Only finished dishes with published price, pack size, nutrition and a HEAD-200 image. No GTIN on bofrost.at → ean None.
Delivery by bofrost* drivers across Austria (Niederlassung Sattledt OÖ); delivery fee not published on the product page → None."""
import json, glob, re, os
STORE = "Online: bofrost*"
DATEN = "/workspace/fertiggerichte-daten/raw"
VEG = re.compile(r"veggie|vegan|vegetarisch|gemüse-lasagne|käsespätzle|spinat|kürbis-ingwer|knoblauchcreme|käse-lauch|zwiebelsuppe|margherita|tondelle|pasta mit grünem|penne 4 käse|maccaroni|broccoli|steinpilz|eierschwammerl|schlutzkrapfen|kasnudeln|minestrone|tomatensuppe|gemüse-eintopf", re.I)
MEAT = re.compile(r"huhn|hühn|hendl|chicken|pute|rind|schwein|speck|schinken|salam|wurst|fleisch|faschiert|lachs|garnel|muschel|fisch|thunfisch|tonno|kalb|reh|wild|leber|bolognese|carbonara|gröstl|cevapcici|bifteki|beuschel|gulasch(?!.*eierschwammerl)|tafelspitz|steak|roulade|grammel|tiroler|rauchkuchl|bami|paella|surbraten|stroganoff|maultaschen|diavola|capricciosa|hawaii|speciale|piadina|jäger|bauerntopf|pfandl|suppentopf|krautfleisch|frittaten|hühnersuppe|gulaschsuppe|bihun|erbsen-eintopf|alt-wiener|kaspress", re.I)

MEAT_ING = re.compile(r"fleisch|huhn|hühn|hähnchen|pute|rind|schwein|kalb|lamm|wild|reh|hirsch|speck|schinken|salami|wurst|würstchen|leber|"
                      r"geflügel|fisch|lachs|thunfisch|garnele|muschel|tintenfisch|sardelle|krabbe|krebs|gelatine|schmalz|grammel|knochen", re.I)

def latest():
    fs = sorted(glob.glob(f"{DATEN}/bofrost_20*.json")); return fs[-1] if fs else None

def rows(path=None):
    path = path or latest()
    if not path: return []
    d = json.load(open(path)); stamp = d["fetched"]; day = stamp[:10]; out = []
    for p in d["products"]:
        n = p["nutrition_100g"]; size = p["size_g"]; x = p["extra"]
        if x.get("image_head") != 200 or not p["price_eur"] or not size or n.get("protein") is None: continue
        pp = round(n["protein"] * size / 100, 1)
        name = p["name"].replace("„", "").replace("“", "").replace('"', "").replace(",,", "").strip()
        ing = re.split(r"Kann (?:Spuren von )?enthalten", x.get("ingredients") or "")[0]  # allergen trace notes are not ingredients
        # veg from the published ingredient list (not the name): any meat/fish/broth/gelatine word → False; none → True; no list → None
        veg = (False if MEAT_ING.search(ing) or MEAT.search(name) else True) if ing else None
        out.append({"name": name, "brand": "bofrost*", "store": STORE, "price_eur": p["price_eur"], "size_g": size,
            "price_per_kg": p["unit_price_eur"] or round(p["price_eur"] / size * 1000, 2), "url": p["source_url"], "image_url": p["image_url"], "ean": None,
            **{f"{k}_100": n.get(k) for k in ("kcal", "protein", "fat", "satfat", "carbs", "sugar", "fiber", "salt")},
            "protein_pack": pp, "kcal_pack": round(n["kcal"] * size / 100) if n.get("kcal") is not None else None,
            "eur_per_10g_protein": round(p["price_eur"] / pp * 10, 2) if pp else None,
            "nutriscore": x.get("nutriscore"), "manufacturer": "bofrost* Austria GmbH (Vertrieb), 6430 Ötztal-Bahnhof, FN 185873v",
            "producer_id": None, "origin": None, "bio": False, "veg": veg, "prep": "Topf/Pfanne/Backrohr (lt. bofrost.at)", "instantpot": None,
            "category": "Online Meal-Prep", "price_source": f"bofrost.at Produktseite (JSON-LD offers.price) {day}", "price_date": day,
            "nut_source": f"bofrost.at Nährwerttabelle pro {x.get('nutrition_per') or '100 g'} {day} ({p['source_url']})",
            "nut_flag": "zubereitet" if "zubereitet" in (x.get("nutrition_per") or "") else None,
            "packaging": x.get("grammage"), "online": True, "available": x.get("availability") == "InStock",
            "storage": "Tiefkühl (TK)", "shelf_life": "TK (−18 °C)", "shipping_eur": None, "portions": x.get("portions"),
            "article_no": p["source_id"], "bofrost_category": p["category"]})
    return out

def merge(path="online_mealprep.json"):
    cur = [r for r in json.load(open(path)) if r.get("store") != STORE]
    new = rows(); json.dump(cur + new, open(path, "w"), ensure_ascii=False, indent=1)
    return len(new)

if __name__ == "__main__":
    print("bofrost rows:", merge())
