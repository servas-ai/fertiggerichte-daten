"""Nah&Frisch AT ready meals (Daten-Squad 2026-10-13T20b) — first products for the Nah&Frisch chain (was 0).
Source (no login/cookies, robots 'Allow: /', tiles under /media/ — /images,/storage never requested):
  food-connectors `nah-frisch` adapter → https://www.nahundfrisch.at/de/aktuelles/angebote-der-woche
  (weekly offer tiles per KW with validity; tiles are images only → tesseract OCR in the connector).
Every field below was additionally verified by eye on the official tile (brand, name, pack text, price, badge, visible
variant packshots); only variants whose packshot is legible on the tile are listed — no guessed varieties.
Nutrition / EAN / pack size come ONLY from an identical product twin already in the dataset (same brand + variety + pack
size from BILLA/MPreis/Gurkerl), cited in nut_source. Inzersdorfer: tile shows '25% billiger' without an absolute price
→ price_eur stays None (Nah&Frisch shelf price unknown; no 25%-of-other-chain guessing).
Appends only new rows (dedupe by store+name) to /workspace/fertig/connectors_new.json atomically; evidence raw/nahfrisch_<slot>.json."""
import json, os, sys, urllib.request
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters import nah_frisch as N
SLOT = "2026-10-13T20b"; TODAY = "2026-10-13"; CN = "/workspace/fertig/connectors_new.json"; SC = "/workspace/fertig/scored.json"
UA = {"User-Agent": "servas-food-connectors/0.1 (+https://servas.ai)"}
def head(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA, method="HEAD"), timeout=20).status == 200
    except Exception: return False
NUT = ("kcal_100", "protein_100", "fat_100", "satfat_100", "carbs_100", "sugar_100", "fiber_100", "salt_100")
TW = {}
for x in json.load(open(SC)): TW[(x.get("store"), x.get("name"), x.get("url"))] = x
def twin(store, name, url):
    t = TW.get((store, name, url)); assert t, (store, name); return t
# tile file stem -> (offer line as printed, badge, [(variant name, twin key)])
V = {
 "ONLINE_KW4142_26_355x455px2": dict(line="iglo Pikante Knödel", pack="versch. Sorten 350-400 g-Pkg.", unit="(100 g = 1,00-1,14)", price=3.99,
     badge="1+1 gratis ab 2 Pkg. je", variants=[("iglo Pikante Knödel Fleischknödel 4 Stück", ("Gurkerl.at", "Iglo Fleischknödel (tiefgekühlt)", "https://www.gurkerl.at/5936-iglo-fleischknoedel-tiefgekuehlt"), 400)]),
 "ONLINE_KW4142_26_355x455px28": dict(line="Inzersdorfer Fertiggerichte oder Suppen", pack="versch. Sorten 400 g-Dose", unit=None, price=None,
     badge="Alle Inzersdorfer Fertiggerichte oder Suppen 25% billiger", variants=[
       ("Inzersdorfer Rindsgulasch", ("MPreis", "Inzersdorfer Rindsgulasch", None), 400),
       ("Inzersdorfer Gulaschsuppe", ("MPreis", "Inzersdorfer Gulaschsuppe", "https://www.mpreis.at/shop/p/inzersdorfer-gulaschsuppe-225710"), 400),
       ("Inzersdorfer Gefüllte Paprika", ("Gurkerl.at", "Inzersdorfer Gefüllte Paprika", "https://www.gurkerl.at/5970-inzersdorfer-gefuellte-paprika"), 400),
       ("Inzersdorfer Weinbeuschel", ("BILLA", "Inzersdorfer Weinbeuschel", "https://shop.billa.at/produkte/inzersdorfer-weinbeuschel-0044757"), 400)]),
 "ONLINE_KW4142_26_355x455px29": dict(line="Knorr Kaiserteller Suppen", pack="versch. Sorten", unit=None, price=1.39, badge=None, variants=[
       ("Knorr Kaiserteller Grießnockerlsuppe", ("BILLA", "Knorr Kaiserteller Grießnockerlsuppe", "https://shop.billa.at/produkte/knorr-kaiserteller-griessnockerlsuppe-0056224"), None),
       ("Knorr Kaiserteller Knoblauchcremesuppe", ("BILLA", "Knorr Kaiserteller Knoblauchcremesuppe", "https://shop.billa.at/produkte/knorr-kaiserteller-knoblauchcremesuppe-006191"), None)]),
}
# MPreis Rindsgulasch twin: resolve url by EAN 9017100001043
for k, x in TW.items():
    if k[0] == "MPreis" and k[1] == "Inzersdorfer Rindsgulasch" and x.get("ean") == "9017100001043":
        V["ONLINE_KW4142_26_355x455px28"]["variants"][0] = ("Inzersdorfer Rindsgulasch", k, 400)
ev = {"slot": SLOT, "page": N.PAGE, "robots": "nahundfrisch.at robots.txt: User-agent * Allow / (Disallow only /build /css /fonts /images /js /storage)", "tiles": [], "rows_added": []}
offers = N.offers(); rows = []
for o in offers:
    stem = o["tile_url"].rsplit("/", 1)[-1].rsplit(".", 1)[0]
    p = N.to_product(o) if stem in V else None
    ev["tiles"].append({**o, "ocr": p.extra if p else None, "used": stem in V})
    if stem not in V: continue
    v = V[stem]; x = p.extra
    assert v["price"] is None or abs((x.get("price_eur") or 0) - v["price"]) < 0.005, ("OCR/visual price mismatch", stem, x.get("price_eur"), v["price"])
    img = o["tile_url"] if head(o["tile_url"]) else None
    for vname, tk, size in v["variants"]:
        t = twin(*tk); sz = size or t.get("size_g")
        price = v["price"]
        rows.append({"name": vname, "brand": vname.split()[0].replace("iglo", "iglo"), "store": "Nah&Frisch", "price_eur": price, "size_g": sz,
            "price_per_kg": round(price * 1000 / sz, 2) if price and sz else None,
            "url": f"{N.PAGE}#kw{o['kw']}-{stem.rsplit('_', 1)[-1]}-{vname.split()[-1].lower()}", "image_url": img,
            "category": t.get("category"), "packaging": t.get("packaging"), "is_meal": True, "ean": t.get("ean"),
            "manufacturer": t.get("manufacturer"), "producer_id": t.get("producer_id"),
            **{k: t.get(k) for k in NUT}, "nutrition_basis": t.get("nutrition_basis"),
            "nut_source": f"identical product twin {t.get('store')} '{t.get('name')}' {t.get('size_g')} g ({t.get('url')}; {t.get('nut_source') or t.get('source_file')})",
            "price_source": (f"food-connectors/nah-frisch {TODAY} (Nah&Frisch 'Angebote der Woche' KW{o['kw']}, gültig {o['valid_from']}–{o['valid_to']}, "
                             f"Flugblatt-Kachel {stem}): Aktionspreis {price} € je Pkg. ('{v['line']}', {v['pack']}{'; ' + v['badge'] if v['badge'] else ''}); "
                             "nur in teilnehmenden Märkten") if price else None,
            "price_date": TODAY if price else None, "offer_price_eur": price, "offer_valid_from": o["valid_from"], "offer_valid_to": o["valid_to"],
            "offer_text": v["badge"], "offer_line": v["line"], "pack_text": v["pack"], "unit_price_text": v["unit"],
            "size_source": "packshot on tile" if size else f"twin {t.get('store')} pack size",
            "delivery": "Nah&Frisch Märkte AT (teilnehmende Kaufleute)", "added_slot": SLOT})
cur = json.load(open(CN)); have = {(r.get("store"), r.get("name")) for r in cur}
new = [r for r in rows if (r["store"], r["name"]) not in have]
if "--write" in sys.argv and new:
    cur = json.load(open(CN)); cur += [r for r in new if (r["store"], r["name"]) not in {(c.get("store"), c.get("name")) for c in cur}]
    tmp = CN + ".tmp_nahfrisch"; json.dump(cur, open(tmp, "w"), ensure_ascii=False, indent=1); os.replace(tmp, CN)
ev["rows_added"] = new
json.dump(ev, open(f"/workspace/fertiggerichte-daten/raw/nahfrisch_{SLOT}.json", "w"), ensure_ascii=False, indent=1)
print(len(offers), "tiles;", len(rows), "rows,", len(new), "new;", [(r["name"], r["price_eur"], r["size_g"], r["kcal_100"], bool(r["image_url"])) for r in new])
