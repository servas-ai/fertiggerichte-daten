"""Append MPreis + Unimarkt ready meals from heisse-preise.io dump into products/prices.
Reuses dishes.dish_key (same classics filter as Hofer/dm) and inlined score.classify for storage.
Never fabricates values; source + fetched_at always set from the dump.
"""
from __future__ import annotations
import csv, hashlib, json, os, re, sys
from datetime import datetime, timezone
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
sys.path.insert(0, "/workspace/fertig")
sys.path.insert(0, "/workspace/food-connectors")

from dishes import dish_key, LABEL, EXCL  # noqa: E402
from food_connectors.adapters.heisse import data as heisse_data  # noqa: E402

def classify(x):
    """Inlined from fertig/score.py classify (avoid module-level I/O side effects)."""
    t = " ".join(str(x.get(k) or "") for k in ["category", "name", "prep", "brand"]).lower()
    nm = (x.get("name") or "").lower(); cat = (x.get("category") or "").lower()
    pk = (x.get("packaging_raw") or "").lower()
    if pk:
        if pk.startswith("tk"): return "Tiefkühl (TK)"
        if pk.startswith("dose"): return "Dose/Konserve"
        if pk.startswith("trocken"): return "Trocken/Instant"
        if pk.startswith("kühl"): return "Kühlregal (Menüschale/frisch)"
    if "sous" in t and "vide" in t: return "Sous-vide (vakuum)"
    if cat.startswith("frozen") or re.search(r"iglo|curly fries|nuggets|cordon bleu|tiefk|\btk\b|gefror|frozen|tiefgek", t) or x.get("source_file") == "ftg_items.json":
        return "Tiefkühl (TK)"
    if re.search(r"\bglas\b|im glas|einmach", t): return "Glas"
    if re.search(r"instant|5 ?min|terrine|cup|becher|pulver|trocken|beutelsuppe|fix für|nudelsnack|ramen|noodle", nm) or "instant" in cat:
        return "Trocken/Instant"
    if re.search(r"little lunch|langbein|steirerkraft|auinger|im glas", t): return "Glas"
    if re.search(r"mikrowell|pouch", nm): return "Beutel ungekühlt (Retort-Pouch)"
    if cat == "beutel" or re.search(r"knorr|maggi|kochbeutel|bouillon|\bfix\b|clever (nudel|buchstaben)suppe|vorratsschrank", t):
        return "Trocken/Instant"
    if re.search(r"dosensuppe|konserv|dose", t): return "Dose/Konserve"
    if cat == "dose" or re.search(r"\bdose\b|konserve|inzersdorfer|eintopf|ravioli in|s-budget rindsgulasch|chili con carne|erasco|sonnen bassermann", t):
        return "Dose/Konserve"
    if cat == "beutel" or "ungekühlt" in cat or re.search(r"beutel|pouch|mikrowellen", t):
        return "Beutel ungekühlt (Retort-Pouch)"
    if cat.startswith("fertiggerichte gek") or cat in ("menüschalen", "frische pasta & beilagen", "asien", "suppen") or re.search(r"good choice|omis|menü|schale|gekühlt|frisch|kühl", t) or cat in ("ready_meal", "dumpling", "fish", "leberkaese", "breaded", "marinated", "skewer", "ribs", "sausage", "raw_meat"):
        return "Kühlregal (Menüschale/frisch)"
    if x.get("source_file") in ("frozen_quick.json",): return "Kühlregal (Menüschale/frisch)"
    return "Unklar (keine Lagerangabe)"

EXTRA = re.compile(
    r"aufstrich|streichcreme|chips|riffel|flips|cracker|keks|camembert|gorgonzola|käse\b(?!.*spätz)|"
    r"schlemmergurken|knoblauch mit|gurken|pickle|sugo\b|ragu'?|pasta.?sauce|"
    r"lasagneblätter|lasagne.?blätter|cannelloni.?röhren|teigwaren|nudeln roh|"
    r"curry.?pulver|curry.?paste|würz|gewürz|seasoning|marinade|ketchup|öl\b|"
    r"hundefutter|katze|whiskas|faschiert$|hackfleisch|gulaschfleisch|"
    r"geschnitten(?!.*fertig)|natur,?\s*geschnitten|frischfleisch|"
    r"butter\b(?! chicken)|milch\b|joghurt|quark|mehl\b|"
    r"^alberto cannelloni|^barilla (emili|la collezione|cannelloni|lasagne(?! .*fertig))",
    re.I,
)
MEAL_HINT = re.compile(
    r"fertig|menü|menu|eintopf|suppentopf|gulasch|chili|lasagne|ravioli|tortellini|cannelloni|"
    r"bolognese|risotto|geschnetzelt|braten|roulade|paprika.?huhn|paprikahendl|cevap|djuvec|"
    r"stroganoff|schmarrn|knödel|fleckerl|spätzle|kasnock|nasi|bami|paella|moussaka|tikka|"
    r"bowl|pfanne|gratin|auflauf|ripperl|reisfleisch|backhendl|backhuhn|tafelspitz|"
    r"\bdal\b|frikassee|ragout|meister ?kessel|5-?minuten|terrine|magic asia|spaghetteria|"
    r"indisches curry|thai.?kokos|soja.?bolognese|hühner-?nudel|linseneintopf|erbseneintopf|"
    r"kichererbsen-?kokos|vegetarische gemüse",
    re.I,
)
VEGAN_RE = re.compile(r"\bvegan|\bveggie|sin carne|vegetar", re.I)
CHAIN = {"mpreis": "MPreis", "unimarkt": "Unimarkt"}

def pid(url: str, name: str, chain: str) -> str:
    return hashlib.sha1(f"{url or ''}|{name}|{chain}".encode()).hexdigest()[:12]

def brand_of(name: str) -> str:
    known = (
        "Good Choice", "Ja! Natürlich", "Alnatura", "Inzersdorfer", "Knorr", "Maggi",
        "Felix", "Barilla", "Little Lunch", "Jeden Tag", "Clever", "S-Budget",
        "Ben's Original", "Bertagni", "Brajlovic", "Kotányi", "Alles Glut", "efko",
        "Erasco", "Sonnen Bassermann",
    )
    for k in known:
        if name.lower().startswith(k.lower()):
            return k
    for pref, brand in (("ALN ", "Alnatura"), ("AHG ", "AHG"), ("AIA ", "AIA"), ("Go ", "Go")):
        if name.startswith(pref):
            return brand
    m = re.match(r"([A-ZÄÖÜ][\wÄÖÜäöüß'’&.-]*(?:\s+[A-ZÄÖÜ][\wÄÖÜäöüß'’&.-]*)?)", name)
    return m.group(1) if m else ""

def is_meal(x: dict) -> str | None:
    name = x.get("name") or ""
    if EXCL.search(name) or EXTRA.search(name):
        return None
    k = dish_key(name)
    if not k:
        return None
    q, u = x.get("quantity"), x.get("unit")
    if u in ("g", "ml") and q is not None:
        if q < 150 or q > 5000:
            return None
    if not MEAL_HINT.search(name):
        return None
    return k

def abs_url(store: str, url: str | None) -> str:
    if not url:
        return ""
    if url.startswith("http"):
        return url
    base = "https://www.unimarkt.at" if store == "unimarkt" else "https://www.mpreis.at"
    return base + (url if url.startswith("/") else "/" + url)

def price_status_for(date: str | None) -> str:
    if not date:
        return "Preis unbestätigt"
    y = date[:4]
    if y >= "2026":
        return "live 2026"
    if y == "2025":
        return "Preis 2025"
    return f"Preis {y}"

def main():
    existing = list(csv.DictReader(open(f"{DATA}/products.csv")))
    existing_prices = list(csv.DictReader(open(f"{DATA}/prices.csv")))
    seen = {r["product_id"] for r in existing}
    seen_names = {(r["chain"], r["name"].strip().lower()) for r in existing}

    new_prods, new_prices = [], []
    for x in heisse_data():
        store = x.get("store")
        if store not in CHAIN:
            continue
        k = is_meal(x)
        if not k:
            continue
        chain = CHAIN[store]
        name = (x.get("name") or "").strip()
        if (chain, name.lower()) in seen_names:
            continue
        url = abs_url(store, x.get("url"))
        i = pid(url, name, chain)
        if i in seen:
            continue
        seen.add(i)
        seen_names.add((chain, name.lower()))

        ph = (x.get("priceHistory") or [{}])[0] or {}
        pdate = ph.get("date") or ""
        qty, unit = x.get("quantity"), x.get("unit")
        size_g = float(qty) if unit in ("g", "ml") and qty is not None else ""
        price = x.get("price")
        ppk = round(price / qty * 1000, 2) if price and qty and unit in ("g", "ml") and qty > 0 else ""

        pack = classify({"name": name, "brand": brand_of(name), "category": ""})
        bio = bool(x.get("bio")) if x.get("bio") is not None else False
        vegan = bool(VEGAN_RE.search(name))

        new_prods.append({
            "product_id": i, "name": name, "brand": brand_of(name), "chain": chain,
            "dish": LABEL.get(k, ""), "storage": pack, "pack_size_g": size_g,
            "producer": "", "origin": "", "bio": bio, "vegan": vegan,
            "url": url, "image_url": "", "source": "heisse-preise.io",
        })
        if price is not None and 0.1 <= float(price) <= 200:
            new_prices.append({
                "product_id": i, "chain": chain, "price_eur": price,
                "price_per_kg_eur": ppk, "price_status": price_status_for(pdate),
                "fetched_at": pdate or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "price_source": f"heisse-preise.io {store} (Preisstand {pdate or '?'}) – Altpreis, nicht live bestätigt",
            })

    pfields = list(existing[0].keys())
    with open(f"{DATA}/products.csv", "a", newline="") as fh:
        w = csv.DictWriter(fh, pfields, extrasaction="ignore")
        for r in new_prods:
            w.writerow({k: ("" if r.get(k) is None else r.get(k, "")) for k in pfields})
    prfields = list(existing_prices[0].keys())
    with open(f"{DATA}/prices.csv", "a", newline="") as fh:
        w = csv.DictWriter(fh, prfields, extrasaction="ignore")
        for r in new_prices:
            w.writerow({k: ("" if r.get(k) is None else r.get(k, "")) for k in prfields})

    all_prods = existing + new_prods
    all_prices = existing_prices + new_prices

    def norm_prod(r):
        out = dict(r)
        for b in ("bio", "vegan"):
            v = out.get(b)
            out[b] = v.strip().lower() in ("true", "1", "yes") if isinstance(v, str) else bool(v)
        if out.get("pack_size_g") in ("", None):
            out["pack_size_g"] = None
        else:
            try: out["pack_size_g"] = float(out["pack_size_g"])
            except (TypeError, ValueError): out["pack_size_g"] = None
        return out

    def norm_price(r):
        out = dict(r)
        try: out["price_eur"] = float(out["price_eur"])
        except (TypeError, ValueError): pass
        if out.get("price_per_kg_eur") in ("", None):
            out["price_per_kg_eur"] = None
        else:
            try: out["price_per_kg_eur"] = float(out["price_per_kg_eur"])
            except (TypeError, ValueError): out["price_per_kg_eur"] = None
        return out

    json.dump([norm_prod(r) for r in all_prods], open(f"{DATA}/products.json", "w"), ensure_ascii=False, indent=1)
    json.dump([norm_price(r) for r in all_prices], open(f"{DATA}/prices.json", "w"), ensure_ascii=False, indent=1)

    print(json.dumps({
        "added_products": len(new_prods),
        "added_prices": len(new_prices),
        "by_chain_products": dict(Counter(r["chain"] for r in new_prods)),
        "by_chain_prices": dict(Counter(r["chain"] for r in new_prices)),
        "totals": {"products": len(all_prods), "prices": len(all_prices)},
        "samples": [{"name": r["name"], "chain": r["chain"], "dish": r["dish"], "url": r["url"]} for r in new_prods[:5]],
    }, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
