"""Fleischerei Buchberger webshop (buchberger.shop; Buchberger GmbH & Co KG, Mittelgasse 39, 8225 Pöllau, Steiermark;
FN 14170p LG für ZRS Graz; UID ATU29190201 VIES valid 2026-10-25T00:39:34Z 'Buchberger GmbH & Co KG, Poellau 39 A, AT-8225 Pöllau')
→ rows 'Online: Fleischerei Buchberger' in data/online_mealprep.csv (idempotent replace) + evidence raw/buchberger_<stamp>.json
+ new company row 'buchberger' (Daten-Squad 2026-10-25T0035).
Source: food-connectors `buchberger` adapter (public JOLIOO shop HTML, robots allow; category 'essen-im-glas' + product
pages at 1 req/s) → 5 jar meals 450 ml. Gulaschsaft, Sugo and Sojabolognese are sauces → excluded.
Nutrition per 100 g exactly as printed (3/5); Hirsch-/Kalbsragout energy does not match Atwater → kept, flagged; Putencurry
values unusually high for a curry but Atwater-consistent → kept, flagged. Size is a volume (450 ml) → per-pack protein/kcal
and €/10 g protein deliberately NOT derived. No GTIN. Photos: main packshot, vision gate 5/5 PASS.
Shipping: Kühlversand, free from 120 €; delivery area and fee below 120 € not published."""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import buchberger as B

CSV = "data/online_mealprep.csv"
N = {"energy_kcal": "kcal_100", "protein_g": "protein_100", "fat_g": "fat_100", "carbs_g": "carbs_100", "sugar_g": "sugar_100"}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in B.Buchberger().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; nut = d.get("nutrition_100g") or {}; at = x.get("atwater")
        if not nut:
            flag = "keine Nährwerte auf der Produktseite → nicht geschätzt"
        elif at and not at["ok"]:
            flag = f"Nährwerte pro 100 g wie veröffentlicht; Energie {nut.get('energy_kcal')} kcal passt nicht zu Atwater ({at['calc_kcal']} kcal aus Makros) → Herstellerangabe unplausibel"
        else:
            flag = "Nährwerte pro 100 g wie veröffentlicht (Atwater-konsistent; Werte für ein Curry ungewöhnlich hoch)"
        flag += "; Inhalt 450 ml Volumen → keine Pro-Packung-Werte abgeleitet; keine GTIN"
        r = {"name": d["name"], "brand": "Buchberger", "store": B.STORE, "price_eur": d["price_eur"], "size_g": 450,
             "price_per_kg": round(d["price_eur"] / 450 * 1000, 2), "url": d["source_url"], "image_url": d["image_url"],
             "manufacturer": B.PRODUCER, "producer_id": "buchberger", "origin": "AT", "bio": False, "veg": False,
             "prep": "Glas im Wasserbad/Topf erwärmen", "category": "Online Meal-Prep",
             "price_source": f"buchberger.shop Produktseite {day}, Preis pro Glas 450 ml inkl. MwSt. (€/kg-Spalte = €/l); Kühlversand, ab 120 € versandkostenfrei, Liefergebiet/Versandkosten darunter nicht veröffentlicht",
             "price_date": day, "nut_source": "Herstellerangabe Produktseite" if nut else "", "packaging": "Glas 450 ml",
             "online": True, "available": True, "storage": x.get("storage") or "",
             "shelf_life": "MHD " + (x.get("mhd") or "").lower(), "shipping_eur": None, "nut_flag": flag, "ean": None, "portions": None}
        for k, c in N.items():
            r[c] = nut.get(k)
        rows.append(r)
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != B.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": B.BASE + B.CATEGORY + " + product pages", "fetched": stamp, "operator": B.PRODUCER,
           "vies": {"uid": "ATU29190201", "valid": True, "name": "Buchberger GmbH & Co KG", "address": "Poellau 39 A, AT-8225 Pöllau", "checked": "2026-10-25T00:39:34Z"},
           "gleif": "no LEI found for 'Buchberger GmbH & Co KG' (2026-10-25)",
           "impressum": B.BASE + "/impressum (Buchberger GmbH & Co KG, Mittelgasse 39, 8225 Pöllau; FN 14170p; LG für ZRS Graz; UID ATU29190201)",
           "shipping": B.SHIPPING_NOTE, "photo_vision_gate": "5/5 PASS (single-jar packshots labelled with the dish name)",
           "excluded": ["Gulaschsaft", "Sugo", "Sojabolognese (Sauce; Nährwerte identisch mit Sugo kopiert)"], "kept": kept}
    json.dump(out, open(f"raw/buchberger_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "buchberger"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "buchberger", "name": "Fleischerei Buchberger", "role": "producer",
        "legal_name": "Buchberger GmbH & Co KG", "fn": "FN 14170p", "register_id": "FN 14170p", "register_authority": "Firmenbuch",
        "country": "AT", "address": "Mittelgasse 39, AT-8225 Pöllau", "founded": "1946 (Unternehmensangabe 'Fleischhauer seit 1946')",
        "website": B.BASE, "product_count": len(rows), "median_price_eur": prices[len(prices) // 2], "fetched_at": out["vies"]["checked"],
        "brands": "Buchberger", "chains": B.STORE, "uid": "ATU29190201", "uid_vies_name": "Buchberger GmbH & Co KG",
        "uid_vies_address": "Poellau 39 A, AT-8225 Pöllau", "uid_checked_at": "2026-10-25T00:39:34.504Z", "imprint_url": B.BASE + "/impressum",
        "register_court": "Landesgericht für ZRS Graz", "registry_status": "verified_vies_imprint"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
