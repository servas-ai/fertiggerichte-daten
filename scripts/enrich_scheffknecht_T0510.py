"""Ariane Scheffknecht webshop (ariane-scheffknecht.at; sole trader Ariane Scheffknecht, Lorettoweg 14, A-6890 Lustenau,
Vorarlberg; Impressum on /datenschutz without UID or Firmenbuch number → no VIES check possible; firmenabc/Creditreform:
'Ariane Maria Scheffknecht', Einzelunternehmen, retail of food since 16.03.2017; GLEIF legalName 'Scheffknecht' → 5 records,
none for Ariane Scheffknecht → no LEI)
→ rows 'Online: Ariane Scheffknecht' in data/online_mealprep.csv (idempotent replace) + evidence raw/scheffknecht_<stamp>.json
+ new company row 'scheffknecht' (Daten-Squad 2026-10-25T0510). No logo staged (no distinct logo file found on the site).
Source: food-connectors `scheffknecht` adapter (public Wix store-products sitemap + product-page schema.org JSON-LD) →
8 hand-made pasteurised jar meals (curries, chilis, dal, Gerstensuppen); Ragù alla Bolognese (pasta sauce) excluded.
No nutrition and no GTIN published → empty, never estimated. 'Gerstensuppe mit Käferbohnen' has no description → size empty.
Photos: primary product photos vision-checked 8/8 PASS (jar/dish of the named meal).
Shipping: 'zzgl. Versand' per product page, homepage 'Ab 12 Gläser versandkostenfrei'; fee not published on the static
pages → shipping_eur empty.
Usage: python3 scripts/enrich_scheffknecht_T0510.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import scheffknecht as S

CSV = "data/online_mealprep.csv"
PRODUCER = "Ariane Scheffknecht (Einzelunternehmen, Lustenau Vbg)"
VEG = {"chili-vegan", "gelbes-zitronengras-linsen-dal", "süßkartoffel-kichererbsen-chili", "gerstensuppe-vegan"}


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in S.Scheffknecht().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]
        flags = ["keine Nährwerte im Shop → nicht geschätzt",
                 f"Zutaten lt. Shop ({x.get('ingredients') or '—'}); keine GTIN",
                 "Versandkosten im Shop nicht ausgewiesen (zzgl. Versand); ab 12 Gläsern versandkostenfrei"]
        if not size: flags.append("Produktseite ohne Beschreibung → Füllmenge/Zutaten nicht veröffentlicht, size_g leer")
        rows.append({"name": d["name"], "brand": "Ariane Scheffknecht", "store": S.STORE, "price_eur": d["price_eur"],
             "size_g": int(size) if size else "", "price_per_kg": round(d["price_eur"] / size * 1000, 2) if size else "",
             "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": PRODUCER, "producer_id": "scheffknecht", "origin": "AT", "bio": False, "veg": d["source_id"] in VEG,
             "prep": "pasteurisiert im Glas – erwärmen (lt. Shop)", "category": "Online Meal-Prep",
             "price_source": f"ariane-scheffknecht.at Wix-Shop {day}, Preis je Glas inkl. USt (schema.org Offer); zzgl. Versand, ab 12 Gläsern versandkostenfrei",
             "price_date": day, "nut_source": "", "packaging": (f"Glas {int(size)} g" if size else "Glas"),
             "online": True, "available": bool(x.get("in_stock")), "storage": "ungekühlt (pasteurisiert)",
             "shelf_life": "mehrere Monate (lt. Shop)", "shipping_eur": "", "nut_flag": "; ".join(flags), "ean": None,
             "portions": x.get("portions") or ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != S.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": S.BASE + "/store-products-sitemap.xml + /product-page/<slug> schema.org Product JSON-LD", "fetched": stamp,
           "operator": PRODUCER, "vies": "no UID published → not checkable",
           "gleif": "GLEIF legalName 'Scheffknecht' → 5 records (Scheffknecht Transporte GmbH, KLÜCKAR Scheffknecht e.U., Scheffknecht Transport AG, INSOMNIA Scheffknecht, Peitler OG, Wilhelm Scheffknecht Stickerei …), none for Ariane Scheffknecht; fuzzy 'Ariane Scheffknecht' → 0 → no LEI",
           "impressum": S.BASE + "/datenschutz (ARIANE SCHEFFKNECHT, Lorettoweg 14, A-6890 LUSTENAU, office@ariane-scheffknecht.at, +43 699 190 05 266; no FN, no UID)",
           "firmenabc": "Ariane Maria Scheffknecht, Einzelunternehmen seit 16.03.2017, Einzelhandel mit Nahrungs- und Genussmitteln",
           "robots": "User-agent: * Allow: / ; Disallow: *?lightbox= (product pages allowed)",
           "shipping": S.SHIPPING_NOTE, "photo_vision_gate": "8/8 PASS",
           "excluded": ["Ragù alla Bolognese (sugo-bolognese; pasta sauce, '3 Portionen (mit Pasta)')"],
           "kept": kept}
    json.dump(out, open(f"raw/scheffknecht_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "scheffknecht"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "scheffknecht", "name": "Ariane Scheffknecht", "role": "producer",
        "legal_name": "Ariane Maria Scheffknecht (Einzelunternehmen)", "legal_form_code": "Einzelunternehmen", "country": "AT",
        "address": "Lorettoweg 14, AT-6890 Lustenau", "entity_status": "keine UID/FN veröffentlicht; kein LEI",
        "founded": "2017-03-16", "owners": "Ariane Maria Scheffknecht", "website": S.BASE, "product_count": len(rows),
        "median_price_eur": prices[len(prices) // 2], "fetched_at": stamp,
        "brands": "Ariane Scheffknecht", "chains": S.STORE, "plants_count": 1, "imprint_url": S.BASE + "/datenschutz",
        "registry_status": "imprint_only_no_uid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
