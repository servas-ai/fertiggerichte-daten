"""Bauernladen.at marketplace — category 'Schnelle Küche' (farm/manufactory heat-up meals, producers ship within AT incl. Linz)
→ evidence raw/bauernladen_<stamp>.json + rows 'Online: Bauernladen.at' in data/online_mealprep.csv (idempotent replace)
+ operator company row (Fundula Medien GmbH, vormals MN Anzeigenservice GmbH) + logo row (Daten-Squad 2026-10-18T0439).

Source: food-connectors `bauernladen` adapter — server-rendered listing /produkte/liste/lebensmittel/schnelle-kueche (4 pages,
79 products) → product pages (schema.org Product JSON-LD price/availability/images/seller + 'Kaufen' pack size + producer
address + the producer's own 'Lieferkonditionen'). robots: only /cgi-bin/, /contact?to=*, /produkte/form-* disallowed.
Kept = heat-up dishes/soups from producers that ship within Austria. Excluded (reason in evidence): Dunzinger's Ruck Zuck
(15 — already indexed from its own shop ruckzuck-laden.at, avoid duplicates), broths/fonds, sauces/sugo, sides/dumplings,
desserts, boxes, powders, cold cuts, Schweinsbraten 2 Scheiben (cold roast slices), and producers whose delivery is limited to a
radius ('Versand in einem Umkreis von 100 km' → Linz not verifiable).
No GTIN published; 3 producers print a 'Nährwerte' line without reference quantity → kept in evidence only, never per-100 g.
Photos: vision-gated on scripts/logo_work_T0439/photo_vision_sheet_{1,2}.jpg — jar packshots with printed dish label PASS;
Venatio styled serving photos (real photography, dish matches) PASS as 'Serviervorschlag'; 3 images rejected as likely
AI-generated illustrations (Venatio Erdäpfelgulasch mit Wildkäsekrainer, Sandriegel Wohlfühlsüppchen + Krautfleckerl) → image empty.
Usage: python3 scripts/enrich_bauernladen_T0439.py [--stamp 2026-10-18T0439] [--pages /tmp/bl/pages]"""
import sys, json, csv, glob, re, datetime, argparse, os
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import bauernladen as B

CSV = "data/online_mealprep.csv"
REJECT_IMG = {"Erdäpfelgulasch mit Wildkäsekrainer", "Exotisches Wohlfühlsüppchen, 450g, eingekocht, vegan", "Krautfleckerl vegan, eingekocht im Glas"}
SERVING_OK = {"venatio-wildspezialitaeten-aus-jaegerhand", "vom-sandriegel"}  # styled dish photos, no pack
NOT_MEAL_EXTRA = re.compile(r"^Schweinsbraten \d Scheiben", re.I)
OPERATOR = {"name": "Fundula Medien GmbH (vormals MN Anzeigenservice GmbH)", "seat": "Brehmstraße 10/4.OG, 1110 Wien",
            "register": "FN 304617t (Handelsgericht Wien) — evi.gv.at: Eingetragen, GmbH, Eintragungsdatum 12.01.2008, Stammkapital EUR 35 000; Namensänderung eingetragen 17.10.2026",
            "vat": "ATU64133538 (VIES valid 2026-10-18, name still 'MN Anzeigenservice GmbH', address 'Brehmstraße 10/OG 4, AT-1110 Wien')",
            "management": "Markus Bauer (Geschäftsführer seit 25.05.2009 lt. evi.gv.at)", "owners": "1 Gesellschafter (natürliche Person, eingetragen 17.10.2026 lt. evi.gv.at)",
            "source": "https://bauernladen.at/seite/impressum"}


def at_shipping(terms):
    """(fee_eur, free_from_eur, min_order_eur) for Austria from the producer's 'Lieferkonditionen' text."""
    if not terms: return None, None, None
    at = terms.split("Deutschland")[0]
    fee = re.search(r"(?:bis [\d.,]+ (?:€|kg Gesamtgewicht): |Kosten für Versand: )([\d.,]+) €", at)
    free = re.search(r"Ab ([\d.,]+) €: Zustellung gratis|Zustellung gratis ab ([\d.,]+) €", at)
    mn = re.search(r"verfügbar ab ([\d.,]+) € Mindestbestellwert|gratis ab ([\d.,]+) € Mindestbestellwert", at)
    f = lambda m: float(next(g for g in m.groups() if g).replace(".", "").replace(",", ".")) if m else None
    return (0.0 if fee is None and free and "gratis ab" in at else f(fee)), f(free), f(mn)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stamp"); ap.add_argument("--pages", default="/tmp/bl/pages"); a = ap.parse_args()
    stamp = a.stamp or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M"); day = stamp[:10]
    kept, excluded, total = [], [], 0
    for fn in sorted(glob.glob(os.path.join(a.pages, "*.html"))):
        total += 1
        p = B.parse_product(open(fn, encoding="utf-8", errors="replace").read())
        if not p: excluded.append({"file": os.path.basename(fn), "reason": "no product JSON-LD"}); continue
        x = p.extra; why = None
        if x["producer_slug"] == "dunzingers-ruck-zuck" or (p.source_url is None and "Dunzinger" in (p.brand or "")):
            why = "Dunzinger's Ruck Zuck — bereits über eigenen Shop ruckzuck-laden.at indexiert (Duplikat)"
        elif not B.is_meal_name(p.name) or NOT_MEAL_EXTRA.search(p.name):
            why = "kein Fertiggericht (Fond/klare Suppe/Soße/Sugo/Beilage/Knödel/Dessert/Box/Pulver/Aufschnitt)"
        elif "Umkreis" in (x.get("delivery_terms") or ""):
            why = "Versand nur im Umkreis (z. B. 100 km) bzw. an Vermarktungstagen — Lieferung nach Linz nicht belegbar"
        elif "Österreich" not in (x.get("ships_to") or "") and "Österreich" not in (x.get("delivery_terms") or "")[:20]:
            why = "kein Versand nach Österreich angegeben"
        if why: excluded.append({"name": p.name, "producer": p.brand, "url": p.source_url, "price_eur": p.price_eur, "reason": why}); continue
        d = p.to_dict(); ok = p.name.strip() not in REJECT_IMG
        kind = None
        if ok: kind = "Serviervorschlag (Produzentenfoto, keine Packung)" if x["producer_slug"] in SERVING_OK else "Glas-Packshot mit gedrucktem Gerichtsnamen"
        if x["producer_slug"] in SERVING_OK and p.name.strip() in {"Rindsgulasch eingekocht, glutenfrei, 400g"}: kind = "Produzentenfoto im Kochtopf (keine Packung)"
        d["extra"]["vision_gate"] = f"PASS ({kind})" if ok else "REJECT (vermutlich KI-generierte Illustration, keine Packung)"
        if not ok: d["image_url"] = None
        kept.append(d)
    rows = []
    for d in kept:
        x = d["extra"]; fl = x["flags"]; brand = re.sub(r"\s+", " ", (d["brand"] or "").replace("„", "").replace("“", "")).strip()
        fee, free, mn = at_shipping(x.get("delivery_terms"))
        veg = "vegan" if fl.get("vegan") or re.search(r"vegan", d["name"], re.I) else ("vegetarisch" if fl.get("vegetarisch") else None)
        stor = "Tiefkühl (TK)" if fl.get("tiefgekühlt") else ("gekühlt" if fl.get("kühlbedürftig") else ("ungekühlt (Glaskonserve)" if fl.get("kühlbedürftig") is False else None))
        size = d["size_g"]
        rows.append({"name": d["name"].strip(), "brand": brand, "store": B.STORE, "price_eur": d["price_eur"], "size_g": size,
            "price_per_kg": round(d["price_eur"] / size * 1000, 2) if size and d["price_eur"] else None,
            "url": d["source_url"], "image_url": d["image_url"], "manufacturer": f"{brand}, {x.get('producer_address') or ''}".strip(", "),
            "origin": "AT" + (f" ({x['producer_address']})" if x.get("producer_address") else ""), "bio": bool(fl.get("bio")), "veg": veg,
            "prep": None, "category": "Online Meal-Prep",
            "price_source": f"bauernladen.at Produktseite (JSON-LD Offer, Preis inkl. MwSt.) {day}; Versand durch den Produzenten" + (f" AT {fee:.2f} €" if fee else "") + (f", frei ab {free:.0f} €" if free else "") + (f", Mindestbestellwert {mn:.0f} €" if mn else ""),
            "price_date": day, "nut_source": None, "packaging": f"{x.get('pack_unit') or ''} {int(size) if size else ''}".strip() or None,
            "online": True, "available": x.get("availability") == "InStock", "storage": stor,
            "shelf_life": f"ca. {x['shelf_life_days']} Tage lt. Produzent" if x.get("shelf_life_days") else None, "shipping_eur": fee,
            "nut_flag": "keine Nährwerte je 100 g auf bauernladen.at (nicht geschätzt)" + ("; Freitext-Nährwerte ohne Bezugsgröße nur in raw evidence" if x.get("nutrition_text") else ""),
            "ean": None, "portions": None})
    cur = list(csv.DictReader(open(CSV, encoding="utf-8"))); cols = list(cur[0].keys())
    cur = [r for r in cur if r["store"] != B.STORE]
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(cur)
        w.writerows({c: ("" if r.get(c) is None else r.get(c)) for c in cols} for r in rows)
    SLUG = "fundula-medien-bauernladen"
    prices = sorted(r["price_eur"] for r in rows)
    vies = json.load(open("/tmp/bl/vies.json"))
    row = {"slug": SLUG, "name": "Bauernladen.at (Fundula Medien GmbH)", "role": "retailer", "legal_name": "Fundula Medien GmbH",
           "lei": None, "fn": "FN 304617t", "register_id": "304617t", "register_authority": None, "legal_form_code": None, "country": "AT",
           "address": "Brehmstraße 10/4.OG, 1110 Wien, AT", "entity_status": "Eingetragen (Firmenbuch, evi.gv.at)", "parent_direct": None, "parent_ultimate": None,
           "founded": "2008-01-12", "owners": "1 Gesellschafter (natürliche Person: Markus Bauer, eingetragen 17.10.2026 lt. evi.gv.at)",
           "employees": None, "revenue": None, "website": "https://bauernladen.at", "product_count": len(rows),
           "median_price_eur": prices[len(prices)//2], "median_eur_per_10g_protein": None, "fetched_at": stamp,
           "brands": ["Bauernladen", "Bauernladen.at"], "chains": ["Bauernladen.at"], "plants_count": 0, "uid": "ATU64133538",
           "uid_vies_name": vies.get("name"), "uid_vies_address": (vies.get("address") or "").replace("\n", ", "), "uid_checked_at": vies.get("requestDate"),
           "imprint_url": "https://bauernladen.at/seite/impressum", "register_court": "Handelsgericht Wien", "hrb": None,
           "registry_status": "verified_vies+impressum+firmenbuch (Impressum 'MN Anzeigenservice GmbH, FN 304617t, ATU64133538' = VIES name+address; evi.gv.at FN 304617t now 'Fundula Medien GmbH' after Namensänderung eingetragen 17.10.2026)"}
    P = "data/companies.json"
    dd = [r for r in json.load(open(P)) if r["slug"] != SLUG]
    dd.append({**row, "former_names": ["MN Anzeigenservice GmbH"], "share_capital": "EUR 35 000", "register_status": "Eingetragen",
               "register_entry_date": "2008-01-12", "management": "Markus Bauer (Geschäftsführer seit 25.05.2009)",
               "nace": "Betrieb einer digitalen Informationsplattform (Marktplatz für Direktvermarkter) lt. Impressum",
               "sources": [OPERATOR["source"], "https://ec.europa.eu/taxation_customs/vies/", "https://www.evi.gv.at/f/304617t"]})
    json.dump(dd, open(P, "w"), ensure_ascii=False, indent=1)
    C = "data/companies.csv"
    cc = list(csv.DictReader(open(C, encoding="utf-8"))); ccols = list(cc[0].keys())
    cc = [r for r in cc if r["slug"] != SLUG]
    o = {c: row.get(c) for c in ccols}; o["brands"] = "|".join(row["brands"]); o["chains"] = "|".join(row["chains"])
    with open(C, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ccols); w.writeheader(); w.writerows(cc)
        w.writerow({k: ("" if v is None else v) for k, v in o.items()})
    LR = {"slug": "bauernladen", "name": "Bauernladen.at", "category": "Handelskette", "file": "logos/bauernladen.png",
          "source_url": "https://s0.bauernladen.at/themes/modern_1/images/BauernladenLogo_20200625.png (bauernladen.at header 'main-logo' 350x220 palette PNG, robots allow; transparency flattened on white, otherwise unmodified; vision gate PASS: chalkboard wordmark 'Bauernladen — Vom Produzenten direkt zu Dir'; file staged in fertiggerichte-daten scripts/logo_work_T0439 for the Orchestrator merge)",
          "brands": ["Bauernladen", "Bauernladen.at", B.STORE, "Fundula Medien GmbH", "MN Anzeigenservice GmbH"]}
    LJ = "data/logos.json"; lj = [r for r in json.load(open(LJ)) if r["slug"] != "bauernladen"]; lj.append(LR)
    json.dump(lj, open(LJ, "w"), ensure_ascii=False, indent=1)
    LC = "data/logos.csv"; lc = list(csv.DictReader(open(LC, encoding="utf-8"))); lcols = list(lc[0].keys())
    lc = [r for r in lc if r["slug"] != "bauernladen"]
    with open(LC, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=lcols); w.writeheader(); w.writerows(lc); w.writerow({**LR, "brands": "|".join(LR["brands"])})
    by_prod = {}
    for r in rows: by_prod[r["brand"]] = by_prod.get(r["brand"], 0) + 1
    out = {"source": "bauernladen.at category 'Schnelle Küche' listing + product pages (food-connectors bauernladen adapter)", "fetched": stamp,
           "robots": "bauernladen.at: User-agent * Disallow only /cgi-bin/, /contact?to=*, /produkte/form-*; polite ≥1 s between requests, no login/cookies/cart",
           "operator": OPERATOR, "vies": vies, "listing_products": total, "kept": len(rows), "by_producer": by_prod,
           "with_photo": sum(bool(r["image_url"]) for r in rows), "with_nutrition_per_100g": 0, "with_gtin": 0,
           "nutrition_free_text": {d["name"]: d["extra"]["nutrition_text"] for d in kept if d["extra"].get("nutrition_text")},
           "excluded": excluded, "products": kept, "logo": LR}
    json.dump(out, open(f"raw/bauernladen_{stamp}.json", "w"), ensure_ascii=False, indent=1)
    print("listing", total, "kept", len(rows), "photos", out["with_photo"], "excluded", len(excluded), "by_producer", by_prod,
          "csv rows", len(cur) + len(rows), "companies", len(dd), "logos", len(lj))

if __name__ == "__main__":
    main()
