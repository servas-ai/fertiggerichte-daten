"""Land-Fleischerei Fichtenbauer webshop (fleischerei-fichtenbauer.at; Land-Fleischerei Fichtenbauer GmbH, Firmensitz
Hauptstraße 12, 3872 Amaliendorf, Filiale Stadtplatz 33, 3950 Gmünd, Waldviertel NÖ; FN 523618b LG Krems an der Donau;
UID ATU74965969 VIES valid 2026-10-25 'Landfleischerei Fichtenbauer GmbH'; GLEIF fulltext 'Fichtenbauer' → 0, no LEI)
→ rows 'Online: Fleischerei Fichtenbauer' in data/online_mealprep.csv (idempotent replace) + evidence
raw/fichtenbauer_<stamp>.json + new company row 'fichtenbauer' (Daten-Squad 2026-10-25T0205).
Source: food-connectors `fichtenbauer` adapter (public Contao HTML, robots disallow only /contao/ and /_contao/;
shop listing + product pages with schema.org microdata, 3 s apart; the site's request-verification page is never
scripted around) → 3 heat-up jar meals 400 g. Excluded: Bolognese Sauce essfertig (sauce), smoked cold cuts sold
'essfertig' (Hauswurzen Bauchfleisch, Karreeroller, Zigeunerspeck), salami/würstel/pastete. No nutrition and no GTIN
published → empty, never estimated. Ingredients as printed on the product page. Photos: vision gate 3/3 PASS (jar
packshots with lid labels Beuschel / Rinds-Gulasch / Wildragout). Shipping: webshop for Austria (AGB 01.10.2024),
10 € flat below 99 €, free from 99 €.
Usage: python3 scripts/enrich_fichtenbauer_T0205.py [stamp] [cached adapter json]  (cached = the adapter's fetch()
output saved during the same run, so the shop is not hit twice)."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import fichtenbauer as F

CSV = "data/online_mealprep.csv"
VIES = {"uid": "ATU74965969", "valid": True, "name": "Landfleischerei Fichtenbauer GmbH",
        "address": "Hauptstraße 12, AT-3872 Amaliendorf", "checked": "2026-10-25T02:07:14.723Z"}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else [p.to_dict() for p in F.Fichtenbauer().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]
        rows.append({"name": d["name"], "brand": "Fichtenbauer", "store": F.STORE, "price_eur": d["price_eur"], "size_g": int(size),
             "price_per_kg": round(d["price_eur"] / size * 1000, 2), "url": d["source_url"], "image_url": d["image_url"],
             "manufacturer": F.PRODUCER, "producer_id": "fichtenbauer", "origin": "AT", "bio": False, "veg": False,
             "prep": "essfertig im Glas – nur erwärmen", "category": "Online Meal-Prep",
             "price_source": f"fleischerei-fichtenbauer.at Produktseite {day} (schema.org Microdata), Preis pro Glas {int(size)} g inkl. MwSt. (Shop-Grundpreis {x.get('unit_price_eur_100g_shop')} €/100 g); Versand-Pauschale 10 € unter 99 €, ab 99 € versandkostenfrei",
             "price_date": day, "nut_source": "", "packaging": f"Glas {int(size)} g", "online": True, "available": True,
             "storage": "", "shelf_life": "", "shipping_eur": F.SHIPPING_EUR,
             "nut_flag": "keine Nährwerte auf der Produktseite → nicht geschätzt; Zutaten lt. Produktseite (" + (x.get("ingredients") or "—") + "); keine GTIN",
             "ean": None, "portions": 1})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != F.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": F.SHOP + " + product pages", "fetched": stamp, "operator": F.PRODUCER, "vies": VIES,
           "gleif": "GLEIF fulltext 'Fichtenbauer' → 0 records (2026-10-25), no LEI",
           "impressum": F.BASE + "/impressum (Land-Fleischerei Fichtenbauer GmbH, Stadtplatz 33, 3950 Gmünd; Firmensitz Hauptstraße 12, 3872 Amaliendorf; UID ATU74965969; FN 523618b; LG Krems an der Donau; Behörde BH Gmünd; GF Hannes Mario Fichtenbauer, Jürgen Markus Fichtenbauer)",
           "robots": "User-agent * Disallow /contao/ /_contao/ only; shop listing and product pages fetched 3 s apart; request-verification page hit twice on images → waited and re-requested, never scripted",
           "shipping": F.SHIPPING_NOTE, "photo_vision_gate": "3/3 PASS (jar packshots, lid labels Beuschel / Rinds-Gulasch / Wildragout)",
           "excluded": ["Bolognese Sauce essfertig (Sauce)", "Hauswurzen Bauchfleisch 900 g 15,30 € (geräucherte Aufschnittware)",
                        "Karreeroller 700 g 14,70 € (geräucherte Aufschnittware)", "Zigeunerspeck 500 g 10,20 € (Speck)",
                        "Salami, Würstel, Pastete, Blunzen etc. (Wurstwaren, kein Fertiggericht)"],
           "kept": kept}
    json.dump(out, open(f"raw/fichtenbauer_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "fichtenbauer"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "fichtenbauer", "name": "Land-Fleischerei Fichtenbauer", "role": "producer",
        "legal_name": "Land-Fleischerei Fichtenbauer GmbH", "fn": "FN 523618b", "register_id": "FN 523618b", "register_authority": "Firmenbuch",
        "legal_form_code": "GmbH", "country": "AT", "address": "Hauptstraße 12, AT-3872 Amaliendorf",
        "entity_status": "UID aktiv (VIES valid); kein LEI", "owners": "GF Hannes Mario Fichtenbauer, Jürgen Markus Fichtenbauer (lt. Impressum)",
        "website": F.BASE, "product_count": len(rows), "median_price_eur": prices[len(prices) // 2], "fetched_at": VIES["checked"],
        "brands": "Fichtenbauer|Land-Fleischerei Fichtenbauer", "chains": F.STORE, "uid": VIES["uid"], "uid_vies_name": VIES["name"],
        "uid_vies_address": VIES["address"], "uid_checked_at": VIES["checked"], "imprint_url": F.BASE + "/impressum",
        "register_court": "Landesgericht Krems an der Donau", "registry_status": "verified_vies_imprint"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
