"""Bernos Tauernwild webshop (bernos.at; Bernos Wildkammer, Inhaber Berno Mühlburger, Oberdrum 20, 9903 Oberlienz,
Osttirol; UID ATU68061919 VIES valid 2026-10-25 name 'Mühlburger Berno Alois', Oberdrum 20, AT-9903 Oberlienz; sole
trader, no Firmenbuch number published; GLEIF fulltext 'Mühlburger' → 1 unrelated German record, no LEI)
→ rows 'Online: Bernos Tauernwild' in data/online_mealprep.csv (idempotent replace) + evidence raw/bernos_<stamp>.json
+ new company row 'bernos' + logo row (Daten-Squad 2026-10-25T0339).
Source: food-connectors `bernos` adapter (public WooCommerce Store API, one request; robots allow all) → 4 heat-up
wild-game jar meals 290 g. No nutrition and no GTIN published → empty, never estimated. Photos vision-checked: 4/4 jar
packshots with matching labels (Reh Ragout, Hirsch Gulasch, Gulaschsuppe vom Wild, Gams Eintopf) PASS.
Shipping (bernos.at/versandarten/): Österreich 5,60 €, Italien/Deutschland 8,50 €; no free-shipping threshold published.
Usage: python3 scripts/enrich_bernos_T0339.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import bernos as B

CSV = "data/online_mealprep.csv"
VIES = {"uid": "ATU68061919", "valid": True, "name": "Mühlburger Berno Alois",
        "address": "Oberdrum 20, AT-9903 Oberlienz", "checked": "2026-10-25T03:43:05.855Z"}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in B.Bernos().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]
        flags = ["keine Nährwerte im Shop → nicht geschätzt",
                 f"Zutaten lt. Shop ({x.get('ingredients') or '—'}); {x.get('meat_share') or ''}; {x.get('free_from') or ''}; keine GTIN"]
        if x["slug"] == "gulaschsuppe-vom-wild":
            flags.append("Kurzbeschreibung 'Glasinhalt 290g', Langtext '300 ml' → 290 g lt. Kurzbeschreibung und Etikett")
        rows.append({"name": d["name"], "brand": "Bernos Tauernwild", "store": B.STORE, "price_eur": d["price_eur"], "size_g": int(size),
             "price_per_kg": d["unit_price_eur"], "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": B.PRODUCER, "producer_id": "bernos", "origin": "AT", "bio": False, "veg": False,
             "prep": "essfertig im Glas – im Topf erhitzen" + (" (" + x["preparation"] + ")" if x.get("preparation") else ""),
             "category": "Online Meal-Prep",
             "price_source": f"bernos.at WooCommerce Store API {day}, Preis je Glas inkl. MwSt.; Versand Österreich 5,60 €",
             "price_date": day, "nut_source": "", "packaging": f"Glas {int(size)} g", "online": True,
             "available": bool(x.get("in_stock")), "storage": "", "shelf_life": "", "shipping_eur": 5.6,
             "nut_flag": "; ".join(flags), "ean": None, "portions": 1})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != B.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": B.BASE + "/wp-json/wc/store/v1/products?per_page=100", "fetched": stamp, "operator": B.PRODUCER, "vies": VIES,
           "gleif": "GLEIF fulltext 'Mühlburger' → 1 record (Autohaus Zschernitz GmbH, Karlsruhe DE, unrelated) (2026-10-25), no LEI",
           "impressum": B.BASE + "/impressum/ (Bernos Wildkammer, Inhaber Berno Mühlburger, A-9903 Oberdrum 20, Tel 0664/5419954, info@bernos.at, UID ATU 68061919)",
           "robots": "Yoast: User-agent * Disallow: (empty) → all allowed; Store API once per call",
           "shipping": B.SHIPPING_NOTE,
           "photo_vision_gate": "4/4 PASS (jar packshots, labels match product names)",
           "logo": "/wp-content/uploads/2016/08/logo.png (alt 'bernos-logo'; white 'berno's TAUERNWILD' wordmark + origami eagle on transparent, for dark backgrounds) → cropped PNG, vision gate PASS",
           "excluded": ["Wildsugo 290 g (pasta sauce)", "Gams-/Hirsch-Henkele 170 g (air-dried meat)", "Die Kleine Rote / Rote / Schwarze Taurer (Dauerwürste)"],
           "kept": kept}
    json.dump(out, open(f"raw/bernos_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "bernos"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "bernos", "name": "Bernos Tauernwild", "role": "producer",
        "legal_name": "Bernos Wildkammer – Berno Mühlburger (Einzelunternehmen)", "legal_form_code": "Einzelunternehmen", "country": "AT",
        "address": "Oberdrum 20, AT-9903 Oberlienz", "entity_status": "UID aktiv (VIES valid); keine FN veröffentlicht; kein LEI",
        "owners": "Inhaber Berno Mühlburger (lt. Impressum)", "website": B.BASE, "product_count": len(rows), "median_price_eur": prices[len(prices) // 2], "fetched_at": VIES["checked"],
        "brands": "Bernos Tauernwild", "chains": B.STORE, "plants_count": 1, "uid": VIES["uid"], "uid_vies_name": VIES["name"],
        "uid_vies_address": VIES["address"], "uid_checked_at": VIES["checked"], "imprint_url": B.BASE + "/impressum/",
        "registry_status": "verified_vies_imprint"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    lp = "data/logos.csv"; lg = list(csv.DictReader(open(lp, encoding="utf-8"))); lcols = list(lg[0].keys())
    lg = [r for r in lg if r["slug"] != "bernos"]
    lg.append({"slug": "bernos", "name": "Bernos Tauernwild", "category": "Markenhersteller", "file": "logos/bernos.png",
        "source_url": "https://www.bernos.at/wp-content/uploads/2016/08/logo.png (site header logo alt 'bernos-logo', white berno's TAUERNWILD wordmark + origami eagle on transparent — needs dark background; robots allow; 370x190 → cropped PNG; vision gate PASS; staged in fertiggerichte-daten scripts/logo_work_T0339 for the Orchestrator merge)",
        "brands": "Bernos Tauernwild|Bernos Wildkammer|Online: Bernos Tauernwild"})
    with open(lp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lg)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
