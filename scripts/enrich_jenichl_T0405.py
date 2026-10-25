"""Genussbauernhof Jenichl farm webshop (genussbauernhof-jenichl.at; Franz & Brigitte Jenichl, Wagham 1, 4950 Altheim,
Innviertel OÖ; Impressum 'Gesellschaftsform: Einzelunternehmen', 'Direktvermarktung, Ab-Hof-Verkauf'; no UID and no
Firmenbuch number published → no VIES check possible; GLEIF fulltext 'Jenichl' → 0 records, no LEI)
→ rows 'Online: Genussbauernhof Jenichl' in data/online_mealprep.csv (idempotent replace) + evidence raw/jenichl_<stamp>.json
+ new company row 'jenichl' + logo row (Daten-Squad 2026-10-25T0405).
Source: food-connectors `jenichl` adapter (public Ecwid storefront catalog JSON, one request) → 4 heat-up jar meals
'essfertig' + 7 frozen Knödel packs. No nutrition and no GTIN published → empty, never estimated. Knödel pack net weight
not published (only Ecwid shipping weight) → size_g empty.
Photos vision-checked: jar meals 4/4 PASS (Gulasch: 2nd picture with 'Gulasch essfertig' label, main picture shows a
Gulaschsaft jar), Surspeck/Spinat/Bärlauch/Tiroler Knödel PASS, Haschee/Grammel/Selchfleisch share one generic plate photo
→ image empty.
Shipping (/zahlung-versand): Österreich via Österreichische Post AG, bis 20 kg 11,50 €, bis 40 kg 17,90 €, ab 40 kg 35 €.
Usage: python3 scripts/enrich_jenichl_T0405.py [stamp]"""
import sys, json, csv, datetime
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import jenichl as J

CSV = "data/online_mealprep.csv"
PRODUCER = "Genussbauernhof Jenichl (Franz & Brigitte Jenichl, Altheim OÖ)"


def main():
    stamp = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept = [p.to_dict() for p in J.Jenichl().fetch()]
    rows = []
    for d in kept:
        x = d["extra"]; size = d["size_g"]; frozen = x["frozen"]
        flags = ["keine Nährwerte im Shop → nicht geschätzt", f"Zutaten lt. Shop ({x.get('ingredients') or '—'}); keine GTIN"]
        if frozen: flags.append("Packungs-Nettogewicht nicht veröffentlicht → size_g leer")
        if x.get("shared_image_url"): flags.append("Shop-Foto identisch mit anderen Knödelsorten (Füllung nicht erkennbar) → kein Bild")
        if d["source_id"] == "241886285": flags.append("Hauptbild zeigt Gulaschsaft-Glas → 2. Shop-Foto (Etikett 'Gulasch essfertig') verwendet")
        rows.append({"name": d["name"], "brand": "Genussbauernhof Jenichl", "store": J.STORE, "price_eur": d["price_eur"],
             "size_g": int(size) if size else "", "price_per_kg": round(d["price_eur"] / size * 1000, 2) if size else "",
             "url": d["source_url"], "image_url": d["image_url"] or "",
             "manufacturer": PRODUCER, "producer_id": "jenichl", "origin": "AT", "bio": False, "veg": "Spinat" in d["name"] or "Bärlauch" in d["name"],
             "prep": ("tiefgekühlt – 12–15 Min. in siedendes Wasser (lt. Shop)" if frozen else "essfertig im Glas – vor dem Verzehr erwärmen (lt. Shop)"),
             "category": "Online Meal-Prep",
             "price_source": f"genussbauernhof-jenichl.at Ecwid-Storefront {day}, Preis inkl. 10 % USt.; Post-Versand AT 11,50 € bis 20 kg",
             "price_date": day, "nut_source": "", "packaging": (f"Glas {int(size)} g" if size else f"Packung {x.get('pieces')} Stk., tiefgekühlt"),
             "online": True, "available": not x.get("sold_out"), "storage": "tiefgekühlt" if frozen else "", "shelf_life": "",
             "shipping_eur": 11.5, "nut_flag": "; ".join(flags), "ean": None, "portions": 1 if size else ""})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != J.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    out = {"source": J.API + "/catalog (POST, categoryViewMode EXPANDED)", "fetched": stamp, "operator": PRODUCER,
           "vies": "no UID published in Impressum → not checkable",
           "gleif": "GLEIF fulltext 'Jenichl' → 0 records (2026-10-25), no LEI",
           "impressum": J.BASE + "/impressum (Genussbauernhof Jenichl, Wagham 1, A-4950 Altheim, Ansprechpartner Franz Jenichl, Gesellschaftsform Einzelunternehmen, Medieninhaber Franz & Brigitte Jenichl, Direktvermarktung/Ab-Hof-Verkauf; no FN, no UID)",
           "robots": "no robots.txt on www.genussbauernhof-jenichl.at nor on eu-fra3-storefront-api.ecwid.com (404 → allow)",
           "shipping": J.SHIPPING,
           "photo_vision_gate": "8/11 PASS; Haschee/Grammel/Selchfleisch Knödel share one generic photo → no image",
           "logo": "Webflow CDN 5f50fa05179a1d7cbb125c89_genussbauernhof-jenichl-logo.png (oval 'Jenichl Spezialitäten ab Hof'), 439x240, vision gate PASS",
           "excluded": ["Gulaschsaft, Pasta Asciutta Sugo, Chili Dip (sauces)", "Semmelknödel 4 Stk. (plain side)", "Speck, Geselchtes",
                        "Rohwürstel, Punkerl Käswurst/Wiener/Polnische/Alpenländer, Knacker, Frankfurter, Depreziner, Blutwurst (sausages)",
                        "Leberkäse, Leberkäse Pikant", "Grammelschmalz, Fleischaufstrich, Leberpastete (spreads)", "Sulz"],
           "kept": kept}
    json.dump(out, open(f"raw/jenichl_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    cp = "data/companies.csv"; comp = list(csv.DictReader(open(cp, encoding="utf-8"))); ccols = list(comp[0].keys())
    comp = [r for r in comp if r["slug"] != "jenichl"]
    prices = sorted(r["price_eur"] for r in rows)
    comp.append({c: "" for c in ccols} | {"slug": "jenichl", "name": "Genussbauernhof Jenichl", "role": "producer",
        "legal_name": "Genussbauernhof Jenichl – Franz & Brigitte Jenichl (Einzelunternehmen lt. Impressum)", "legal_form_code": "Einzelunternehmen", "country": "AT",
        "address": "Wagham 1, AT-4950 Altheim", "entity_status": "keine UID/FN veröffentlicht (Direktvermarkter); kein LEI",
        "owners": "Franz & Brigitte Jenichl (Medieninhaber lt. Impressum)", "website": J.BASE, "product_count": len(rows),
        "median_price_eur": prices[len(prices) // 2], "fetched_at": stamp,
        "brands": "Genussbauernhof Jenichl", "chains": J.STORE, "plants_count": 1, "imprint_url": J.BASE + "/impressum",
        "registry_status": "imprint_only_no_uid"})
    with open(cp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(comp)
    lp = "data/logos.csv"; lg = list(csv.DictReader(open(lp, encoding="utf-8"))); lcols = list(lg[0].keys())
    lg = [r for r in lg if r["slug"] != "jenichl"]
    lg.append({"slug": "jenichl", "name": "Genussbauernhof Jenichl", "category": "Markenhersteller", "file": "logos/jenichl.png",
        "source_url": "https://cdn.prod.website-files.com/5f15b77ace47805abb4fa379/5f50fa05179a1d7cbb125c89_genussbauernhof-jenichl-logo.png (site header logo; oval 'Jenichl Spezialitäten ab Hof' on transparent; 439x240; vision gate PASS; staged in fertiggerichte-daten scripts/logo_work_T0405 for the Orchestrator merge)",
        "brands": "Genussbauernhof Jenichl|Online: Genussbauernhof Jenichl"})
    with open(lp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lg)
    print("kept", len(kept), "online meal-prep", sum(1 for r in cur if r.get("category") == "Online Meal-Prep") + len(rows))


main()
