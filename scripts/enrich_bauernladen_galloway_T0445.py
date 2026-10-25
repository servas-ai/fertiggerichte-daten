"""Bauernladen.at — Bio Galloway Hof Kerschbaumlehen (Hubberg 13, 3341 Ybbsitz NÖ): Rindsbeuscherl 1 kg, 36 € (Daten-Squad 2026-10-25T0445).
Re-check of all 78 'Schnelle Küche' tiles vs. data: unindexed items are sugo/fond/sides/desserts/boxes, Dunzinger's offers that duplicate
own-shop rows (policy of T0439/T1811), Danke Bauer 'Schweinsbraten 2 Scheiben' (meat component, excluded T1811) and this one meal.
Chilled, Bio flag; delivery only on the producer's marketing days (03.07./02.10./04.12.2026) within 100 km, 17 € below 150 € (min. 50 €).
Photo: generic 'Fertiggerichte' placeholder graphic → vision gate FAIL, no image. No GTIN/nutrition → never estimated."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import bauernladen as B
CSV = "data/online_mealprep.csv"
stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
p = B.product("https://bauernladen.at/produkte/bio-galloway-hof-kerschbaumlehen/rindsbeuscherl-44259"); x = p.extra
row = {"name": p.name, "brand": p.brand, "store": B.STORE, "price_eur": p.price_eur, "size_g": p.size_g,
       "price_per_kg": round(p.price_eur / p.size_g * 1000, 2), "url": p.source_url, "image_url": None,
       "manufacturer": "Bio Galloway Hof Kerschbaumlehen, Hubberg 13, 3341 Ybbsitz Niederösterreich", "origin": "AT (Hubberg 13 3341 Ybbsitz Niederösterreich)",
       "bio": bool(x["flags"].get("bio")), "veg": None, "category": "Online Meal-Prep",
       "price_source": f"bauernladen.at Produktseite (JSON-LD Offer, Preis inkl. MwSt.) {day}; Zustellung durch den Produzenten nur an Vermarktungstagen (03.07./02.10./04.12.2026) im Umkreis 100 km, Mindestbestellwert 50 €, 17 € bis 149,99 €, frei ab 150 €; Abholung möglich",
       "price_date": day, "packaging": "g 1000", "online": True, "available": x.get("availability") == "InStock",
       "storage": "gekühlt", "shelf_life": None, "shipping_eur": 17.0,
       "nut_flag": "keine Nährwerte je 100 g auf bauernladen.at (nicht geschätzt); Foto: generische 'Fertiggerichte'-Grafik (vision gate FAIL); Lieferung nur Umkreis 100 km an 3 Terminen/Jahr"}
cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
cur = [r for r in cur if r["url"] != row["url"]]
with open(CSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
    w.writerow({c: ("" if row.get(c) is None else row.get(c)) for c in cols})
json.dump({"source": "bauernladen.at product page", "fetched": stamp, "added": p.__dict__,
           "vision_gate": "FAIL — generic Fertiggerichte placeholder graphic used for many producers"},
          open(f"raw/bauernladen_galloway_{stamp}.json", "w"), ensure_ascii=False, indent=1, default=str)
print("csv rows", len(cur) + 1)
