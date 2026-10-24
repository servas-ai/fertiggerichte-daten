"""Bauernladen.at — Dunzinger's Ruck Zuck jars that are NOT in Dunzinger's own shop ruckzuck-laden.at
(Daten-Squad 2026-10-24T1811; COVERAGE open item 'other Bauernladen categories with ready meals').
T0439 skipped all 15 Dunzinger's offers on bauernladen.at as duplicates of the own-shop rows. A re-check against the live
ruckzuck-laden.at Ecwid storefront (17 articles, 7 meals) shows 3 Bauernladen-only meals: Rehragout vom heimischen Wild,
Hirschragout vom heimischen Wild (370 g, 9,50 €) and BBQ Kokos Eintopf VEGAN (330 ml, 8,40 €). They are added as
'Online: Bauernladen.at' rows (sold + shipped by the producer via Bauernladen: AT 8,90 €, free from 100 €; Hermes).
Photos: none taken. Reh/Hirsch use the same generic image of three Gulasch jars (wrong dish → vision gate FAIL);
BBQ Kokos Eintopf uses a marketing flyer composite (jar + styled bowl + ingredient cut-outs → not a product photo, FAIL).
No GTIN / nutrition published → never estimated. Name says VEGAN; the page's 'Vegan' flag says Nein → veg left empty, conflict noted.
Other Bauernladen categories re-checked via b2c_offer-sitemap.xml (14 254 offers, keyword pass): only raw meat (Gulaschfleisch,
Lammragout roh), spice blends ('… Gerichte 120g', 'Hirten Gulasch'), dry risotto mixes that need extra ingredients, and the
Danke Bauer 'Schweinsbraten 2 Scheiben' (meat component, no sides) → no further ready meals."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import bauernladen as B
from food_connectors.adapters import ruckzuck as R

CSV = "data/online_mealprep.csv"
IDS = ["dunzingers-ruck-zuck/rehragout-vom-heimischen-wild-34056", "dunzingers-ruck-zuck/hirschragout-vom-heimischen-wild-35638",
       "dunzingers-ruck-zuck/bbq-kokos-eintopf-vegan-45297"]
stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
own = [p.name for p in R.RuckZuck()._all()]
norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())
ps = [B.product("https://bauernladen.at/produkte/" + i) for i in IDS]
ps = [p for p in ps if p and not any(norm(p.name.split(" vom ")[0]) == norm(o.split(" vom ")[0]) for o in own)]
rows = []
for p in ps:
    x = p.extra
    rows.append({"name": p.name, "brand": "Dunzinger's Ruck Zuck", "store": B.STORE, "price_eur": p.price_eur,
        "size_g": p.size_g, "price_per_kg": round(p.price_eur / p.size_g * 1000, 2) if p.size_g else None,
        "url": p.source_url, "image_url": None,
        "manufacturer": "Schimpl OG, Guttenbrunn 18, 4242 Hirschbach im Mühlkreis, FN 306047w",
        "origin": "AT (Guttenbrunn 18 4242 Hirschbach Oberösterreich)" + ("; Wild aus Jagd Leopoldschlag (OÖ) lt. Zutaten" if "Leopoldschlag" in (x.get("ingredients_text") or "") else ""),
        "bio": False, "veg": None, "category": "Online Meal-Prep",
        "price_source": f"bauernladen.at Produktseite (JSON-LD Offer, Preis inkl. MwSt.) {day}; Versand durch den Produzenten AT 8.90 €, frei ab 100 €",
        "price_date": day, "packaging": f"{p.unit} {int(p.size_g)}" if p.size_g else "Glas", "online": True,
        "available": x.get("availability") == "InStock", "storage": "ungekühlt (Glaskonserve)",
        "shelf_life": f"ca. {x['shelf_life_days']} Tage lt. Bauernladen" if x.get("shelf_life_days") else None, "shipping_eur": 8.9,
        "nut_flag": "keine Nährwerte je 100 g auf bauernladen.at (nicht geschätzt); Foto: kein produktspezifisches Bild (vision gate FAIL)"
                    + ("; Name 'VEGAN', Seitenflag Vegan: Nein → veg leer" if "VEGAN" in p.name else "")})
cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
urls = {r["url"] for r in rows}
cur = [r for r in cur if r["url"] not in urls]
with open(CSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
    w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
json.dump({"source": "bauernladen.at product pages (food-connectors bauernladen adapter)", "fetched": stamp,
           "own_shop_meals_checked": own, "added": [p.to_dict() if hasattr(p, "to_dict") else p.__dict__ for p in ps],
           "vision_gate": {"rehragout/hirschragout": "FAIL — shared image shows three 'Gulasch vom Mühlviertler Rindvieh' jars in a pot",
                           "bbq-kokos-eintopf": "FAIL — marketing flyer composite (jar + styled bowl + ingredient cut-outs)"},
           "sitemap_recheck": "b2c_offer-sitemap.xml 14254 URLs, keyword pass 361 → no further ready meals outside 'Schnelle Küche'"},
          open(f"raw/bauernladen_dunzinger_{stamp}.json", "w"), ensure_ascii=False, indent=1, default=str)
print("added", len(rows), "csv rows", len(cur) + len(rows))
