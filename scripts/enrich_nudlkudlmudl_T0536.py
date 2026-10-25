"""Martina's Nudlkudlmudl (nudlkudlmudl.com; Martina Hinteregger, Hauptstrasse 28, 9545 Radenthein, Kärnten; Impressum /about/
without UID or Firmenbuch number → no VIES check possible; GLEIF legalName 'Hinteregger' → 18 records, none in Radenthein and
none for Martina Hinteregger / Nudlkudlmudl; fuzzy 'Nudlkudlmudl' → 0 → no LEI; AMA-certified Nudelmanufaktur since 08/2022)
→ rows 'Online: Martina's Nudlkudlmudl' in data/online_mealprep.csv (idempotent replace) + evidence raw/nudlkudlmudl_<stamp>.json
+ new company row 'nudlkudlmudl' (Daten-Squad 2026-10-25T0536). No logo staged.
Source: food-connectors `nudlkudlmudl` adapter (one public Jimdo /onlineshop/ page, schema.org Product microdata) → 7 ready meals:
6 hand-made filled Kärntner Nudeln 600 g / 5 Stk. (cook before eating) + Kärntner Schweinsbraten essfertig 250 g.
Excluded: Kletzennudel (sweet), Bratlfett (spread), Oma's Glasl Kuchl Sugo Bolognese (pasta sauce).
No nutrition and no GTIN published → empty, never estimated.
Photos: primary product photos vision-checked 7/7 PASS (cut-open noodles with the named filling; roast pork for Schweinsbraten).
Shipping: Post Frischeversand AT only, cooled box, free from 100 €; fee = Post tariff 1:1 (shop banner: 19,90 € per parcel since
1.1.2026); the shop's shipping table is on robots-disallowed /j/ → shipping_eur empty.
Usage: python3 scripts/enrich_nudlkudlmudl_T0536.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import nudlkudlmudl as N

CSV = "data/online_mealprep.csv"
PRODUCER = "Martina's Nudlkudlmudl (Martina Hinteregger, Radenthein Ktn)"
MEAT = ("fleischnudel", "schweinsbraten")


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    page = N.get(N.SHOP, raw=True, headers={"Accept": "text/html"}, timeout=40).decode("utf-8", "replace")
    allb = N.blocks(page)
    kept = [p.to_dict() for p in N.all_products(page)]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; roast = "schweinsbraten" in d["source_id"]
        flags = ["keine Nährwerte im Shop → nicht geschätzt",
                 f"Zutaten lt. Shop ({x.get('ingredients') or '—'}); keine GTIN",
                 "Versandkosten = Post-Frischeversand-Tarif 1:1 (lt. Shop seit 1.1.2026 19,90 €/Paket), Tabelle robots-gesperrt → leer; ab 100 € versandkostenfrei"]
        rows.append({"name": d["name"], "brand": "Martina's Nudlkudlmudl", "store": N.STORE, "price_eur": d["price_eur"],
             "size_g": int(size) if size else "", "price_per_kg": d["unit_price_eur"] or "",
             "url": N.SHOP, "image_url": d["image_url"] or "",
             "manufacturer": PRODUCER, "producer_id": "nudlkudlmudl", "origin": "AT", "bio": False,
             "veg": not any(m in d["source_id"] for m in MEAT),
             "prep": ("gebraten, vakuumiert – erwärmen (lt. Shop 'Essfertig')" if roast else "frisch, handgekrendelt – in Salzwasser kochen (Faustnudeln)"),
             "category": "Online Meal-Prep",
             "price_source": f"nudlkudlmudl.com Jimdo-Onlineshop {day}, Preis je Packung inkl. MwSt (schema.org Offer); zzgl. Versand, ab 100 € versandkostenfrei",
             "price_date": day, "nut_source": "", "packaging": ("vakuumiert 250 g" if roast else (x.get("menge") or "")),
             "online": True, "available": bool(x.get("in_stock")), "storage": "gekühlt (Post Frischeversand mit Kühlpads)",
             "shelf_life": "", "shipping_eur": "", "nut_flag": "; ".join(flags), "ean": None,
             "portions": ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != N.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": N.SHOP + " (Jimdo, schema.org Product microdata; 1 request)", "fetched": stamp,
           "operator": PRODUCER, "vies": "no UID published → not checkable",
           "gleif": "legalName 'Hinteregger' → 18 records (e.g. Hinteregger Handelsges.m.b.H. Wernberg, Abschleppdienst Hinteregger GmbH Krumpendorf), none in Radenthein / for Martina Hinteregger; fuzzy 'Nudlkudlmudl' → 0 → no LEI",
           "impressum": "https://www.nudlkudlmudl.com/about/ (Anbieter: Martina Hinteregger, Hauptstrasse 28, 9545 Radenthein, Tel. 0699 11929024; no FN, no UID)",
           "ama": "footer: 'Seit August 2022 sind wir nun eine AMA Zertifizierte Nudelmanufaktur'",
           "robots": "User-agent: * Disallow: /app/ /j/ (Allow /app/module/webproduct/goto/), Crawl-Delay 5 → /onlineshop/ allowed, /j/shop/info not read",
           "shipping": N.SHIPPING_NOTE, "photo_vision_gate": "7/7 PASS",
           "all_shop_products": [{k: b[k] for k in ("name", "price", "in_stock", "size_g")} for b in allb],
           "excluded": ["Kärntner Kletzennudel (sweet, Dörrbirne/Honig/Rum)", "Bratlfett Hausgemacht (spread)", "Oma`s Glasl Kuchl Sugo Bolognese (pasta sauce)"],
           "kept": kept}
    json.dump(out, open(f"raw/nudlkudlmudl_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "nudlkudlmudl"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "nudlkudlmudl", "name": "Martina's Nudlkudlmudl", "role": "producer",
        "legal_name": "Martina Hinteregger (Einzelunternehmen, 'Martina's Nudlkudlmudl')", "legal_form_code": "Einzelunternehmen", "country": "AT",
        "address": "Hauptstrasse 28, AT-9545 Radenthein", "entity_status": "keine UID/FN veröffentlicht; kein LEI; AMA-zertifiziert seit 08/2022",
        "owners": "Martina Hinteregger", "website": N.BASE, "product_count": len(rows),
        "median_price_eur": prices[len(prices) // 2], "fetched_at": stamp,
        "brands": "Martina's Nudlkudlmudl", "chains": N.STORE, "plants_count": 1, "imprint_url": N.BASE + "/about/",
        "registry_status": "imprint_only_no_uid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
