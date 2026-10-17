"""Nah&Frisch AT, Daten-Squad 2026-10-17T2004: weekly re-run of the offer page (Nah&Frisch has no webshop / full assortment,
so rows accumulate week by week). Source: food-connectors `nah-frisch` → https://www.nahundfrisch.at/de/aktuelles/angebote-der-woche
(robots 'Allow: /'; tiles under /media/ only; no login/cookies). New this week: KW43 tab (gültig 2026-10-21–2026-10-27).
Every field was checked by eye on the official tile; only variants whose packshot is legible on the tile are listed:
  - iglo Mehlspeistraum 'Süße Knödel' tile: packshot = iglo 8 Marillenknödel mit ganzen Marillen ohne Kern 530 g
  - Knorr 'Bitte zu Tisch Suppen' tile: packshots = Fleischklößchen Suppe, Grießnockerl Suppe
Price: both tiles print ONLY a multi-buy price ('Günstiger! Ab 2 Pkg. je 4,79' / 'Ab 3 Beutel je 1,09'); the single-pack
shelf price is not printed → no price row (multi-buy guard, same rule as Penny T21); the offer is kept in `source`.
Nutrition / EAN / pack size ONLY from the identical product already in the dataset (same brand + variety + pack size), cited.
Writes data/{products,nutrition}.{csv,json} (append, dedupe chain+name) + data/supplemental/* and raw/nahfrisch_2026-10-17T2004.json."""
import csv, json, os, hashlib, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOT, TODAY, CHAIN = "2026-10-17T2004", "2026-10-17", "Nah&Frisch"
PAGE = "https://www.nahundfrisch.at/de/aktuelles/angebote-der-woche"
TILE = "https://www.nahundfrisch.at/media/cache/resize_w500/Angebote_der_Woche/KW4344/{}.png"
ev = json.load(open(os.environ.get("EV", "/tmp/nf/ev.json")))
V = [  # (tile stem, offer line, pack text, badge, variant name, twin product_id, url slug)
 ("ONLINE_KW4344_26_355x455px", "iglo Mehlspeistraum Süße Knödel", "versch. Sorten 375-530 g-Pkg. (1 kg = 9,04-12,77)", "Günstiger! Ab 2 Pkg. je 4,79 €",
  "iglo Mehlspeistraum 8 Marillenknödel mit ganzen Marillen ohne Kern", "9b920234f8c3", "marillenknoedel"),
 ("ONLINE_KW4344_26_355x455px26", "Knorr Bitte zu Tisch Suppen", "versch. Sorten", "Günstiger! Ab 3 Beutel je 1,09 €",
  "Knorr Bitte zu Tisch Fleischklößchen Suppe", "c9616c44fd49", "fleischkloesschen"),
 ("ONLINE_KW4344_26_355x455px26", "Knorr Bitte zu Tisch Suppen", "versch. Sorten", "Günstiger! Ab 3 Beutel je 1,09 €",
  "Knorr Bitte zu Tisch Grießnockerl Suppe", "cfdc5ddfcda1", "griessnockerl"),
]
P = {r["product_id"]: r for r in json.load(open(f"{R}/data/products.json"))}
N = {r["product_id"]: r for r in json.load(open(f"{R}/data/nutrition.json"))}
tiles = {p["source_id"]: p for p in ev["products"]}
prods, nuts = [], []
for stem, line, pack, badge, name, tw, slug in V:
    t = P[tw]; o = tiles.get(stem); assert o and o["extra"]["kw"] == 43, stem
    url = f"{PAGE}#kw43-{stem.rsplit('_', 1)[-1]}-{slug}"
    i = hashlib.sha1((url + "|" + name + "|" + CHAIN).encode()).hexdigest()[:12]
    prods.append({"product_id": i, "name": name, "brand": t["brand"] or name.split()[0], "chain": CHAIN, "dish": t.get("dish"),
        "storage": t["storage"], "pack_size_g": t["pack_size_g"], "producer": t.get("producer"), "origin": t.get("origin"),
        "bio": t.get("bio"), "vegan": t.get("vegan"), "url": url, "image_url": TILE.format(stem),
        "source": (f"food-connectors/nah-frisch {TODAY}: Nah&Frisch 'Angebote der Woche' KW43 (gültig {o['extra']['valid_from']}–{o['extra']['valid_to']}), "
                   f"Kachel {stem} '{line}', {pack}; Angebot nur als Mehrkaufpreis '{badge}' (Einzelpreis nicht angegeben → kein Preis); "
                   f"nur in teilnehmenden Märkten; EAN/Packung/Nährwerte vom identischen Produkt {t['chain']} '{t['name']}' ({t['url']})"),
        "ean": t.get("ean") or None})
    n = N.get(tw)
    if n: nuts.append({**{k: n[k] for k in n if k not in ("product_id", "eur_per_10g_protein", "health_score", "nutri_score")}, "product_id": i,
                       "nutri_score": None, "health_score": None, "eur_per_10g_protein": None})
def load_csv(n): return list(csv.DictReader(open(f"{R}/data/{n}.csv")))
have = {(r["chain"], r["name"].strip().lower()) for r in load_csv("products")}
new = [r for r in prods if (r["chain"], r["name"].strip().lower()) not in have]
keep = {r["product_id"] for r in new}
add = {"products": new, "nutrition": [r for r in nuts if r["product_id"] in keep]}
if "--write" in sys.argv:
    for n, rows in add.items():
        if not rows: continue
        fields = list(load_csv(n)[0].keys())
        with open(f"{R}/data/{n}.csv", "a", newline="") as fh:
            w = csv.DictWriter(fh, fields, extrasaction="ignore")
            for r in rows: w.writerow(r)
        js = json.load(open(f"{R}/data/{n}.json")); js += rows
        json.dump(js, open(f"{R}/data/{n}.json", "w"), ensure_ascii=False, indent=1)
        sp = f"{R}/data/supplemental/{n}.json"; sj = json.load(open(sp)) if os.path.exists(sp) else []
        ids = {r["product_id"] for r in sj}; sj += [r for r in rows if r["product_id"] not in ids]
        json.dump(sj, open(sp, "w"), ensure_ascii=False, indent=1)
    out = {"slot": SLOT, "page": PAGE, "connector_snapshot": ev, "rows_added": add,
           "not_added": [{"tile": "ONLINE_KW4344_26_355x455px25", "name": "Knorr Goldaugen Rind-, Gemüse- oder Klare Suppen Würfel", "reason": "Suppenwürfel/Brühe, kein Fertiggericht"},
                         {"tile": "KW42 Inzersdorfer + Kaiserteller", "reason": "already in dataset since T20b (same KW42 tiles)"}],
           "price_rule": "multi-buy price only on tile → no price row (single-pack shelf price unknown)"}
    json.dump(out, open(f"{R}/raw/nahfrisch_{SLOT}.json", "w"), ensure_ascii=False, indent=1)
print({k: len(v) for k, v in add.items()})
for r in new: print(" ", r["product_id"], r["name"], r["pack_size_g"], r["ean"], r["storage"])
