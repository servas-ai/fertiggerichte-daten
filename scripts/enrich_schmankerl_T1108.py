"""Schmankerl Österreich (schmankerl-oesterreich.at, Shopify; operator per Impressum/AGB: Pamela Plüschke – Salzburg
Spezialitäten, Einzelunternehmen, Wenigaschau 1, 5143 Feldkirchen; Steuernummer 232/3461; no UID and no Firmenbuch
number published → no VIES check possible; GLEIF no LEI) — online reseller of Innviertel/Austrian regional products,
chilled shipping AT/DE/IT/EU (Mon/Tue dispatch; free from 80 € AT / 100 € EU; fee below that not published).
Source: food-connectors `schmankerl` (Shopify products.json, 1 request: price incl. MwSt., Inhalt, Zutaten, Allergene,
Herkunft, Lagerung, stock, photos). Photos vision-checked: 9/9 real dish photos/packshot; Speckknödel uses image #2
because image #1 duplicates the Spinat-Speck-Knödel photo. Gulaschsuppe = FELIX can on the photo (brand from photo).
No nutrition, no GTIN, no manufacturer published → empty (never estimated).
Excluded: Innviertler Leberknödel (Suppeneinlage), 6er Innviertler Knödel-Mix 1800 g (Bundle), Rotkraut/Sauerkraut
(Beilagen), Probier-Pakete (Bundles), sausages, Leberkäse, cured meat, cheese, jams, condiments, sweets, drinks.
Usage: python3 scripts/enrich_schmankerl_T1108.py [stamp]"""
import sys, json, csv, datetime, re
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import schmankerl as M

CSV = "data/online_mealprep.csv"
SLUG = "schmankerl-oesterreich"
VEG = {"kaeseknoedel", "rote-bete-knoedel", "spinatknoedel", "kaspressknoedel"}  # no meat in the published Zutaten


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    prods = M.Schmankerl().fetch()
    kept = [p.to_dict() for p in prods]
    rows = []
    for d in kept:
        x = d["extra"]; h = x["handle"]; size = d["size_g"]
        flags = ["Preis inkl. MwSt. lt. Shopify-Storefront", "keine Nährwerte publiziert", "keine GTIN publiziert",
                 "Hersteller nicht publiziert (Partnerbetriebe lt. Shop)"]
        if x["content"]:
            flags.append("Inhalt lt. Shop: " + x["content"])
        if size is None:
            flags.append("kein Nettogewicht publiziert")
        if x["ingredients"]:
            flags.append("Zutaten lt. Shop: " + x["ingredients"][:160])
        if h == "gulaschsuppe":
            flags.append("Marke FELIX lt. Produktfoto (Dose); Inhalt 400 g lt. Beschreibung")
        if h == "speckknoedel":
            flags.append("Foto #2 verwendet (Foto #1 = Spinat-Speck-Knödel-Bild)")
        if not x["available"]:
            flags.append(f"ausverkauft lt. Shop {day}")
        st = x["storage"] or ""
        life = re.search(r"mindestens\s+\d+\s+Tage\s+haltbar", st)
        storage = "ungekühlt (Konserve, Dose lt. Produktfoto)" if h == "gulaschsuppe" else (
            ("gekühlt (" + re.sub(r"^Gekühlt\s*", "", st.split(",")[0]) + " lt. Shop)") if st else "")
        rows.append({"name": d["name"], "brand": d["brand"], "store": M.STORE, "price_eur": d["price_eur"],
             "size_g": size or "", "price_per_kg": d["unit_price_eur"] or "", "url": d["source_url"],
             "image_url": d["image_url"] or "", "manufacturer": "", "producer_id": "",
             "origin": ("AT (" + d["origin"] + " lt. Shop)") if d.get("origin") else "",
             "bio": False, "veg": h in VEG,
             "prep": {"Suppe": "Konserve; erhitzen", "Strudel": "vorgegart; im Ofen bei 180 °C erwärmen (lt. Shop)"}.get(x["kind"], "gekocht, gekühlt; erwärmen (lt. Shop)"),
             "category": "Online Meal-Prep",
             "price_source": f"schmankerl-oesterreich.at Shopify-Storefront {day} (inkl. MwSt., zzgl. Versand); {M.SHIPPING_NOTE}",
             "price_date": day, "nut_source": "", "packaging": "Dose" if h == "gulaschsuppe" else "",
             "online": True, "available": bool(x["available"]), "storage": storage,
             "shelf_life": life.group(0) + " (gekühlt, lt. Shop)" if life else "", "shipping_eur": "",
             "nut_flag": "; ".join(flags), "ean": "", "portions": "",
             "protein_pack": "", "kcal_pack": "", "eur_per_10g_protein": ""})
    for r in rows:
        if r["origin"]:
            r["origin"] = r["origin"].replace("AT (Österreich lt. Shop)", "AT (lt. Shop)")
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != M.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": "https://schmankerl-oesterreich.at/products.json?limit=250 (Shopify storefront, 1 request)",
           "fetched": stamp, "robots": "Shopify default robots.txt (disallows cart/checkout/account/sort-filter only)",
           "operator": "Pamela Plüschke – Salzburg Spezialitäten (Einzelunternehmen)",
           "fn": "keine Firmenbuchnummer publiziert (Einzelunternehmen)", "uid": "keine UID publiziert → keine VIES-Prüfung möglich",
           "impressum": {"https://schmankerl-oesterreich.at/policies/legal-notice":
                         "Pamela Plüschke – Salzburg Spezialitäten; Inhaberin Pamela Plüschke; Wenigaschau 1, 5143 Feldkirchen; Tel +43 660 1931984; Mitglied WKO; Aufsichtsbehörde BH Salzburg-Umgebung",
                         "https://schmankerl-oesterreich.at/policies/terms-of-service": "Steuernummer 232/3461"},
           "gleif": "legalName 'Plüschke' → only 'Plüschke & Plüschke GmbH' / 'Walter Plüschke Industrie- Marketing & Vertriebs-GmbH' (unrelated); fulltext 'Schmankerl Österreich' → none → no LEI",
           "shipping": {"AGB §8": "Versand ausschließlich Montag & Dienstag; AT 1–4 Werktage, DE & IT 3–7, EU max. 10",
                        "home page": "kostenloser Versand ab 80 € in Österreich und ab 100 € in ganz Europa",
                        "about page": "Kühlversand in temperaturstabiler Verpackung", "fee below threshold": "nicht publiziert"},
           "photo_vision_gate": "9/9 PASS — real dish photos (Knödel, Strudel) + FELIX Gulaschsuppe can; Speckknödel image #1 duplicate of Spinat-Speck photo → image #2 used",
           "excluded": ["Innviertler Leberknödel 330 g = Suppeneinlage", "6er Innviertler Knödel-Mix 1800 g = Bundle",
                        "Rotkraut mit Apfel, Sauerkraut = Beilagen", "Probier-Pakete = Bundles",
                        "Würste, Leberkäse, Speck, Käse, Marmeladen, Senf/Kren, Kürbiskernöl, Rumkugeln, Bier = keine Fertiggerichte"],
           "kept": kept}
    json.dump(out, open(f"raw/schmankerl_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != SLUG]
    ap = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": SLUG, "name": "Schmankerl Österreich (schmankerl-oesterreich.at)", "role": "retailer",
        "legal_name": "Pamela Plüschke – Salzburg Spezialitäten (Einzelunternehmen)", "legal_form_code": "Einzelunternehmen",
        "country": "AT", "address": "Wenigaschau 1, AT-5143 Feldkirchen",
        "entity_status": "keine UID/FN publiziert (Steuernummer 232/3461 lt. AGB); kein LEI",
        "owners": "Pamela Plüschke lt. Impressum", "website": "https://schmankerl-oesterreich.at", "product_count": len(rows),
        "median_price_eur": ap[len(ap) // 2], "fetched_at": stamp, "brands": "Schmankerl Österreich; Felix", "chains": M.STORE,
        "imprint_url": "https://schmankerl-oesterreich.at/policies/legal-notice", "registry_status": "imprint_no_uid_no_fn"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
