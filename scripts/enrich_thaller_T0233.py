"""Fleischhauerei Thaller webshop (fleischhauerei-thaller.at; Fleischhauerei Thaller – Eduard Thaller, Hauptstraße 34,
8311 Markt Hartmannsdorf, Bezirk Weiz, Steiermark; UID ATU74028946 VIES valid 2026-10-25 'Thaller Eduard Franz',
Hauptstraße 34/2; sole trader, no Firmenbuch number published; GLEIF fulltext → 0, no LEI)
→ rows 'Online: Fleischhauerei Thaller' in data/online_mealprep.csv (idempotent replace) + evidence
raw/thaller_<stamp>.json + new company row 'thaller' (Daten-Squad 2026-10-25T0233).
Source: food-connectors `thaller` adapter (public WooCommerce Store API, one request; robots allow) → category
'Speisen im Glas' → 1 chilled heat-up jar meal (Rindsgulasch im Glas 350 g, 7,50 €). Excluded: Rindssuppe im Glas
1000 ml (clear broth), Leberkäse / Käseleberkäse im Glas (raw meat loaf to bake 45 min, Wurstware). No nutrition and
no GTIN published → empty, never estimated. Ingredients as printed. Photo: the shop's own jar packshot (IMG_7305,
vision gate PASS: jar on board, unlabelled lid); the first shop image is a serving photo (gulasch in bowl), kept as
second image only. Shipping (versandarten): Post within Austria, 18,90 € up to 150 €, 10,90 € up to 250 €, free from 250 €.
Usage: python3 scripts/enrich_thaller_T0233.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import thaller as T

CSV = "data/online_mealprep.csv"
VIES = {"uid": "ATU74028946", "valid": True, "name": "Thaller Eduard Franz",
        "address": "Hauptstraße 34/2, AT-8311 Markt Hartmannsdorf", "checked": "2026-10-25T02:35:17.355Z"}
PACKSHOT = "https://fleischhauerei-thaller.at/wp-content/uploads/2025/08/IMG_7305.jpg"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in T.Thaller().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]
        img = PACKSHOT if PACKSHOT in x["images"] else d["image_url"]
        rows.append({"name": d["name"], "brand": "Fleischhauerei Thaller", "store": T.STORE, "price_eur": d["price_eur"], "size_g": int(size),
             "price_per_kg": round(d["price_eur"] / size * 1000, 2), "url": d["source_url"], "image_url": img,
             "manufacturer": T.PRODUCER, "producer_id": "thaller", "origin": "AT", "bio": False, "veg": False,
             "prep": "essfertig im Glas – nur erwärmen (Mikrowelle oder Topf)", "category": "Online Meal-Prep",
             "price_source": f"fleischhauerei-thaller.at WooCommerce Store API {day}, Preis pro Glas {int(size)} g inkl. 10 % MwSt.; Versand Post AT 18,90 € bis 150 €, 10,90 € bis 250 €, ab 250 € versandkostenfrei",
             "price_date": day, "nut_source": "", "packaging": f"Glas {int(size)} g", "online": True, "available": bool(x.get("in_stock")),
             "storage": "gekühlt 2–4 °C", "shelf_life": "60 Tage", "shipping_eur": 18.9,
             "nut_flag": "keine Nährwerte auf der Produktseite → nicht geschätzt; Zutaten lt. Produktseite (" + (x.get("ingredients") or "—") + "); keine GTIN",
             "ean": None, "portions": 1})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != T.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": T.BASE + "/wp-json/wc/store/v1/products?per_page=100", "fetched": stamp, "operator": T.PRODUCER, "vies": VIES,
           "gleif": "GLEIF fulltext 'Thaller Hartmannsdorf' and legalName 'Thaller Eduard' → 0 records (2026-10-25), no LEI",
           "impressum": T.BASE + "/impressum/ (Fleischhauerei Thaller - Eduard Thaller, Hauptstraße 34, 8311 Markt Hartmannsdorf; UID ATU74028946; no FN)",
           "robots": "User-agent * disallows only wp-admin, WC upload/log folders and ?add-to-cart=; Store API fetched once",
           "shipping": T.SHIPPING_NOTE, "photo_vision_gate": "1/1 PASS (IMG_7305 jar packshot; Gulasch-bea-kw-15-1 = serving photo, second image)",
           "excluded": ["Rindssuppe im Glas 1000 ml 8,00 € (klare Suppe/Brühe)", "Leberkäse im Glas 350 g 6,00 € (roher Leberkäse zum Backen, Wurstware)",
                        "Käseleberkäse im Glas 350 g 6,60 € (roher Leberkäse zum Backen, Wurstware)",
                        "Leberstreichwurst, Verhackert, Grammelschmalz im Glas (Aufstriche)"],
           "leads_closed": {"Fleischerei Metzker Wien": "fleischerei-metzker.at/online-shop: Hauszustellung nur 1160/1170/1180 Wien (7 €, frei ab 50 €) bzw. Abholung – kein Versand nach Linz/AT → nicht aufgenommen"},
           "kept": kept}
    json.dump(out, open(f"raw/thaller_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "thaller"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "thaller", "name": "Fleischhauerei Thaller", "role": "producer",
        "legal_name": "Eduard Thaller (Fleischhauerei Thaller, Einzelunternehmen)", "country": "AT",
        "address": "Hauptstraße 34/2, AT-8311 Markt Hartmannsdorf", "legal_form_code": "Einzelunternehmen",
        "entity_status": "UID aktiv (VIES valid); keine FN im Impressum; kein LEI", "owners": "Eduard (Franz) Thaller (lt. Impressum/VIES)",
        "website": T.BASE, "product_count": len(rows), "median_price_eur": prices[len(prices) // 2], "fetched_at": VIES["checked"],
        "brands": "Fleischhauerei Thaller|Familie Thaller", "chains": T.STORE, "uid": VIES["uid"], "uid_vies_name": VIES["name"],
        "uid_vies_address": VIES["address"], "uid_checked_at": VIES["checked"], "imprint_url": T.BASE + "/impressum/",
        "registry_status": "verified_vies_imprint"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
