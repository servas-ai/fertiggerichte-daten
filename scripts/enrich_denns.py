"""denn's BioMarkt AT ready meals (Daten-Squad 2026-10-13T20).
Sources (no login/cookies, robots-allowed):
  1. food-connectors `denns` adapter — public AT offer feed denns-biomarkt.at/page-data/angebote/page-data.json (land=at):
     ready meals/desserts among the current weekly offers; price_eur = Normalpreis (priceb, shelf price on the feed date),
     Aktionspreis + validity kept in offer_* fields; image = official images.dennree.de/<itemno> (HEAD-verified 200).
  2. Open Food Facts products tagged store "Denn's Biomarkt" + country Austria (no price; nutrition as given on OFF).
Appends only new rows (dedupe by store+name) to /workspace/fertig/connectors_new.json atomically; evidence raw/denns_<slot>.json."""
import json, os, sys, urllib.request, datetime as dt
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters.denns import Denns, FEED
SLOT = "2026-10-13T20"; TODAY = "2026-10-13"; CN = "/workspace/fertig/connectors_new.json"
UA = {"User-Agent": "servas-food-connectors/0.1 (+https://servas.ai)"}
def head(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA, method="HEAD"), timeout=20).status == 200
    except Exception: return False
META = {  # classification from the offer title only (no guessing of variants)
 "564131": dict(category="Suppe/Eintopf", packaging="Konserve/Dose/Glas", is_meal=True),
 "004476": dict(category="Paniert/Nuggets", packaging="Tiefkühl (TK)", is_meal=True),
 "003115": dict(category="TK-Fisch", packaging="Tiefkühl (TK)", is_meal=True),
 "187749": dict(category="Mehlspeisen/Desserts", packaging="Kühlregal (Menüschale/frisch)", is_meal=False),
}
rows, ev = [], {"slot": SLOT, "feed": FEED, "offers": [], "off": [], "rejected": []}
for p in Denns().fetch("all", 500):
    d = p.to_dict(); m = META.get(p.source_id)
    if not m: ev["rejected"].append({"itemno": p.source_id, "name": p.name, "reason": "not a ready meal (offer feed)"}); continue
    x = d["extra"]; img = p.image_url if head(p.image_url) else None
    rows.append({"name": p.name, "brand": p.brand, "store": "denn's BioMarkt", "price_eur": x["regular_price_eur"], "size_g": p.size_g,
        "price_per_kg": round(x["regular_price_eur"] * 1000 / p.size_g, 2) if p.size_g and x["regular_price_eur"] else None,
        "url": f"https://www.denns-biomarkt.at/angebote/#artikel-{p.source_id}", "image_url": img, **m,
        "price_source": f"food-connectors/denns {TODAY} (denn's BioMarkt AT Angebote-Feed, Artikel {p.source_id}): Normalpreis {x['regular_price_eur']} €; Aktionspreis {x['offer_price_eur']} € gültig {x['valid_from']}–{x['valid_to']}" + (" (ab-Preis, mehrere Sorten)" if x["price_from"] else "") + f"; Packung {x['pack']}",
        "price_date": TODAY, "offer_price_eur": x["offer_price_eur"], "offer_valid_from": x["valid_from"], "offer_valid_to": x["valid_to"],
        "pack_text": x["pack"], "denns_itemno": p.source_id, "vegan": x["vegan"], "vegetarian": x["vegetarian"],
        "nut_source": None, "ean": None, "manufacturer": None, "delivery": "denn's BioMarkt Filialen AT (Linz)", "added_slot": SLOT})
    ev["offers"].append(d)
for ean in ("4000345046486", "4000345045328"):
    u = f"https://world.openfoodfacts.org/api/v2/product/{ean}?fields=product_name,brands,quantity,image_front_url,nutriments,stores,countries,nutrition_data_per"
    o = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))["product"]
    if "denn" not in (o.get("stores") or "").lower() or "Austria" not in (o.get("countries") or ""):
        ev["rejected"].append({"ean": ean, "reason": "OFF store/country tag missing"}); continue
    n = o["nutriments"]; g = lambda k: n.get(k + "_100g")
    rows.append({"name": f"{o['brands'].split(',')[0]} {o['product_name']}", "brand": o["brands"].split(",")[0], "store": "denn's BioMarkt",
        "price_eur": None, "size_g": None, "pack_text": o.get("quantity"), "url": f"https://world.openfoodfacts.org/product/{ean}",
        "image_url": o.get("image_front_url") if head(o.get("image_front_url")) else None,
        "kcal_100": g("energy-kcal"), "protein_100": g("proteins"), "fat_100": g("fat"), "satfat_100": g("saturated-fat"), "carbs_100": g("carbohydrates"),
        "sugar_100": g("sugars"), "fiber_100": g("fiber"), "salt_100": g("salt"), "nutrition_basis": "prepared",
        "nut_source": f"Open Food Facts {ean} (Nährwerte je 100 ml zubereitet lt. OFF; Trockensuppe {o.get('quantity')}), {TODAY}",
        "category": "Suppe/Eintopf", "packaging": "Trocken/Instant", "is_meal": True, "ean": ean, "manufacturer": None,
        "price_source": None, "price_date": None, "delivery": "denn's BioMarkt (OFF stores tag, Austria)", "added_slot": SLOT})
    ev["off"].append({"ean": ean, **o})
cur = json.load(open(CN)); have = {(r.get("store"), r.get("name")) for r in cur}
new = [r for r in rows if (r["store"], r["name"]) not in have]
if "--write" in sys.argv and new:
    cur = json.load(open(CN)); cur += [r for r in new if (r["store"], r["name"]) not in {(c.get("store"), c.get("name")) for c in cur}]
    tmp = CN + ".tmp_denns"; json.dump(cur, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, CN)
ev["rows_added"] = new
json.dump(ev, open(f"/workspace/fertiggerichte-daten/raw/denns_{SLOT}.json", "w"), ensure_ascii=False, indent=1)
print(len(rows), "rows,", len(new), "new;", [(r["name"], r["price_eur"], bool(r["image_url"])) for r in new])
