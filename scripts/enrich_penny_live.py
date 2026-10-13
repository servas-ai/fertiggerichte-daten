"""PENNY Österreich ready meals: live 2026 prices + photos + new rows from penny.at's public JSON (never fabricated).
Daten-Squad 2026-10-13T21.

Source: food-connectors `penny-shop` adapter → https://www.penny.at/api/product-discovery/products (the online-assortment
JSON the penny.at shop loads itself; robots.txt = Sitemap only, no login/cookies). ~450 items incl. weekly offers.
Price rule (single-pack price, like the SPAR overlay): price_eur = price.regular when it is a plain single-pack price
(also 'pt-aktion' discounts → price_regular_eur = Normalpreis); for multi-buy offers (promotionType PER_SET_OF, or FROM
with quantity > 1, e.g. 'bei 2 Packungen', 'bei 3 Dosen') the per-unit promo price is NOT a single-pack price →
price_eur = price.standard (Normalpreis), offer kept in offer_* fields. Pack-size guard: never overwrite when the Penny
pack differs > 5 % from the row's size_g. Penny publishes no GTIN/nutrition; multi-variant offers ('div. Sorten',
'… od. …') get NO nutrition (variant unknown).

Writes:
  raw/penny_<slot>.json                        evidence (whole listing summary, every decision)
  /workspace/fertig/penny_live_overlay.json    {rewe_article: live price fields} — applied in score.py before price_status
  /workspace/fertig/connectors_new.json        new PENNY ready-meal rows (atomic, dedupe by store+url) with --write
"""
import json, os, re, sys, datetime as dt
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters.penny_shop import listing, to_product, API  # noqa: E402

SLOT = "2026-10-13T21"; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FERTIG = "/workspace/fertig"; CN = FERTIG + "/connectors_new.json"; OV = FERTIG + "/penny_live_overlay.json"
ART = re.compile(r"penny\.at/produkte/[^?#]*-78(\d{5,7})\b")
# New ready meals (classification from Penny name/category + visual check of the official pack photo; brand only where
# Penny lists it or it is printed on the pack photo → brand_source)
NEW = {
 "785625": dict(name="Podravka Rindergulasch", brand="Podravka", brand_source="Packungsfoto penny.at (Penny-Listing ohne Marke)", category="Fertiggericht", packaging="Konserve/Dose/Glas"),
 "790129": dict(name="Ich bin Österreich Wiener Schnitzel vom Schwein", brand="Ich bin Österreich", category="TK-Gericht", packaging="Tiefkühl (TK)"),
 "913024": dict(name="Dr. Oetker Ristorante Pizza 2er (div. Sorten)", brand="Dr. Oetker", brand_source="Packungsfoto penny.at ('Ristorante', 2 x Pizza, 1+1 gratis)", category="Pizza", packaging="Tiefkühl (TK)"),
 "463664": dict(name="Gabelkönig Semmelknödel-Rolle", brand="Gabelkönig", category="Beilage/Gemüse", packaging="Kühlregal (Menüschale/frisch)"),
 "303260": dict(name="Maggi Magic Asia Instantnudeln (div. Sorten)", brand="Maggi", category="Asien", packaging="Trocken/Instant"),
 "443582": dict(name="Taste Of Asia Knuspergarnelen", brand="Taste Of Asia", category="TK-Fisch", packaging="Tiefkühl (TK)"),
 "420861": dict(name="Heinz Baked Beans", brand="Heinz", category="Klassiker", packaging="Konserve/Dose/Glas"),
 "619544": dict(name="Iglo Fischstäbchen (od. Backfisch-Stäbchen / Polardorsch Knusperhülle)", brand="Iglo", category="TK-Fisch", packaging="Tiefkühl (TK)"),
}
REJECT = {"112012": "Iglo Polardorsch div. Sorten — variants include plain fillets, not clearly a ready meal",
          "690709": "PENNY READY Eierspätzle/Schupfnudeln/Gnocchi/Knöpfle — plain side-dish pasta, 4 variants",
          "107921": "Maggi Würze — seasoning", "284508": "Knorr Brühe/Bouillon — stock", "599272": "Iglo Pommes/Kroketten — side dish"}

def price_rec(r, p, day):
    pr = r.get("price") or {}; reg = pr.get("regular") or {}; std = (pr.get("standard") or {}).get("value")
    multi = reg.get("promotionType") == "PER_SET_OF" or (reg.get("promotionType") == "FROM" and (reg.get("promotionQuantity") or 1) > 1)
    single = (std / 100) if (multi and std) else p.price_eur
    if multi and not std: return None
    return dict(price_eur=single, offer_price_eur=p.price_eur if multi else None, offer_text=reg.get("promotionText"),
                price_regular_eur=(std / 100) if std and not multi and std / 100 != p.price_eur else None,
                valid_from=pr.get("validityStart"), valid_to=pr.get("validityEnd"), multi_buy=multi,
                price_per_kg=round(single * 1000 / p.size_g, 2) if p.size_g and single else None, pack=p.extra.get("pack"),
                penny_name=p.name, image_url=p.image_url, url=p.source_url, sku=p.source_id,
                price_source=f"food-connectors/penny-shop {day} (penny.at Online-Sortiment JSON, Artikel {p.source_id})"
                             + (f"; Mehrfachkauf-Aktion {p.price_eur} € {reg.get('promotionText')} → Einzelpreis = Normalpreis" if multi else ""))

def main():
    now = dt.datetime.now(dt.timezone.utc); stamp, day = now.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y-%m-%d")
    raw = listing(); by = {r["sku"].split("-")[-1]: r for r in raw}
    items = json.load(open(FERTIG + "/scored.json"))
    penny = [x for x in items if "penny" in (x.get("store") or "").lower()]
    ov = {"source": API, "updated_at": stamp, "articles": {}}; ev = dict(slot=SLOT, fetched_at=stamp, source=API, listing_total=len(raw), existing=[], new=[], rejected=[])
    for x in penny:
        m = ART.search(x.get("url") or "")
        if not m: ev["existing"].append(dict(name=x["name"], url=x.get("url"), decision="no penny.at article (OFF/brandfam row) → not in online assortment, unchanged")); continue
        a = m.group(1); r = by.get(a)
        if not r: ev["existing"].append(dict(name=x["name"], article=a, decision="not listed in penny.at online assortment today → unchanged")); continue
        p = to_product(r); rec = price_rec(r, p, day)
        if x.get("size_g") and p.size_g and abs(p.size_g - float(x["size_g"])) / float(x["size_g"]) > 0.05:
            ev["existing"].append(dict(name=x["name"], article=a, decision=f"skip: pack size mismatch {x['size_g']} vs {p.extra.get('pack')}")); continue
        ov["articles"][a] = {**rec, "fetched_at": stamp}
        ev["existing"].append(dict(name=x["name"], article=a, old_price=x.get("price_eur"), new_price=rec["price_eur"], multi_buy=rec["multi_buy"], decision="live"))
    have_urls = {x.get("url") for x in penny}
    rows = []
    for a, meta in NEW.items():
        r = by.get(a)
        if not r: ev["rejected"].append(dict(article=a, reason="not listed today")); continue
        p = to_product(r); rec = price_rec(r, p, day)
        if p.source_url in have_urls or not rec: ev["rejected"].append(dict(article=a, reason="already in dataset or no single-pack price")); continue
        ov["articles"][a] = {**rec, "fetched_at": stamp}
        rows.append({"name": meta["name"], "brand": meta["brand"], "store": "PENNY", "price_eur": rec["price_eur"], "size_g": p.size_g,
            "price_per_kg": rec["price_per_kg"], "url": p.source_url, "image_url": p.image_url, "category": meta["category"],
            "packaging": meta["packaging"], "packaging_hint": meta["packaging"], "is_meal": True, "origin": p.extra.get("origin"),
            "price_source": rec["price_source"], "price_date": day, "price_regular_eur": rec["price_regular_eur"],
            "offer_price_eur": rec["offer_price_eur"], "offer_text": rec["offer_text"], "offer_valid_from": rec["valid_from"], "offer_valid_to": rec["valid_to"],
            "pack_text": p.extra.get("pack"), "variants": p.extra.get("variants"), "penny_sku": p.source_id, "penny_name": p.name,
            "brand_source": meta.get("brand_source"), "nut_source": None, "ean": None, "manufacturer": None, "producer_id": None,
            "delivery": "PENNY Filialen Linz (Filialkauf)", "added_slot": SLOT})
    for a, why in REJECT.items(): ev["rejected"].append(dict(article=a, name=(by.get(a) or {}).get("name"), reason=why))
    ev["new"] = rows; ev["overlay_n"] = len(ov["articles"])
    json.dump(ov, open(OV + ".tmp", "w"), ensure_ascii=False, indent=1); os.replace(OV + ".tmp", OV)
    if "--write" in sys.argv and rows:
        cur = json.load(open(CN)); seen = {(c.get("store"), c.get("url")) for c in cur}
        cur += [r for r in rows if ("PENNY", r["url"]) not in seen]
        json.dump(cur, open(CN + ".tmp_penny", "w"), ensure_ascii=False, indent=1); os.replace(CN + ".tmp_penny", CN)
    json.dump(ev, open(os.path.join(ROOT, "raw", f"penny_{SLOT}.json"), "w"), ensure_ascii=False, indent=1)
    print("overlay", len(ov["articles"]), "new", len(rows), [(r["name"], r["price_eur"]) for r in rows])
    print([(e["name"], e.get("old_price"), e.get("new_price"), e["decision"][:30]) for e in ev["existing"]])

if __name__ == "__main__":
    main()
