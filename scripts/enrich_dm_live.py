"""dm ready meals: live 2026 prices + new products from dm's own public product JSON (never fabricated).

Access order (official JSON first, no login, no cookies):
  1. https://www.dm.at/product-sitemap.xml (robots-allowed; dm.at /search is disallowed → not used)
  2. https://products.dm.de/product/products/detail/AT/dan/{dan} — the JSON the dm.at product page renders.
Only products whose dm breadcrumb is "Ernährung > Fertiggerichte & Konserven" (meals, Schnelle Gerichte,
Suppen & Eintöpfe; plain Konserven/sauces excluded) are taken. Price, pack size, nutrition table (per 100 g/ml),
ingredients, origin and the first non-AI image (GET-verified) come straight from that JSON.

Writes:
  raw/dm_live_YYYY-MM-DD.json            evidence (every probed DAN + decision)
  /workspace/fertig/dm_live.json         live rows (score.py LIVE source; existing rows updated in place by DAN)
  /workspace/fertig/qa/dm_live_fixes.json  excludes heisse-preise Altpreis rows that duplicate a live dm.at product
"""
from __future__ import annotations
import json, os, re, time, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")
FERTIG = "/workspace/fertig"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 ServasFoodResearch/1.0"
API = "https://products.dm.de/product/products/detail/AT/dan/{dan}"
# sitemap slug prefilter (cheap); the dm breadcrumb below is the actual decision
SLUG = re.compile(r"fertiggericht|eintopf|suppe|bowl|ravioli|gulasch|curry|chili|dal\b|lasagne|nudel-tasse|baked-beans|risotto|bolognese")
SLUG_NOT = re.compile(r"gewuerz|tee-|sauce-|paste|katze|hund|shampoo|duft|kerze|pulver|baby|kinder|kids|ab-\d|monat|smoothie|cups|aufstrich|riegel|reis-|risottoreis|lipgloss|nagellack|chips|waffeln|cashew|knabber|pesto|mariniert|nudeln-")
KEEP_CRUMB = ("Ernährung", "Fertiggerichte & Konserven")
DROP_SUB = {"Konserven"}           # plain canned veg/legumes = not a meal
DROP_NAME = re.compile(r"bolognese|topping", re.I)  # pasta sauces

def get(url, raw=False):
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,*/*"}), timeout=30)
    b = r.read(); return (b, r.headers.get("content-type") or "") if raw else json.loads(b)

def num(s):
    m = re.search(r"(\d+(?:[.,]\d+)?)", s or ""); return float(m.group(1).replace(",", ".")) if m else None

def size_g(title, a11y):
    m = re.search(r"(\d+(?:,\d+)?)\s*(g|kg|ml|l)\b", title or "", re.I) or re.search(r"Grundpreis:\s*(\d+(?:,\d+)?)\s*(g|kg|ml|l)\b", a11y or "", re.I)
    if not m: return None
    v = float(m.group(1).replace(",", ".")); return round(v * 1000) if m.group(2).lower() in ("kg", "l") else round(v)

def group(d, header):
    for g in d.get("descriptionGroups") or []:
        if g.get("header") == header: return g.get("contentBlock") or []
    return []

def nutrition(d):
    out, basis = {}, None
    for b in group(d, "Nährwerte"):
        for row in b.get("table") or []:
            if len(row) < 2: continue
            k, v = row[0].lower(), row[1]
            if k.startswith("durchschnittliche"): basis = v; continue
            if k.startswith("brennwert"):
                m = re.search(r"(\d+(?:[.,]\d+)?)\s*kcal", v); out["kcal_100"] = float(m.group(1).replace(",", ".")) if m else None
            elif "gesättigte" in k: out["satfat_100"] = num(v)
            elif k.startswith("fett"): out["fat_100"] = num(v)
            elif "zucker" in k: out["sugar_100"] = num(v)
            elif k.startswith("kohlenhydrate"): out["carbs_100"] = num(v)
            elif "ballast" in k: out["fiber_100"] = num(v)
            elif k.startswith("eiweiß") or k.startswith("eiweiss"): out["protein_100"] = num(v)
            elif k.startswith("salz"): out["salt_100"] = num(v)
    return out, basis

def texts(d, header):
    return " ".join(t for b in group(d, header) for t in (b.get("texts") or [])).strip() or None

def verify(url):
    try:
        b, ct = get(url, raw=True); return ct.startswith("image/") and len(b) > 1000, ct, len(b)
    except Exception as e:
        return False, type(e).__name__, 0

def main():
    now = datetime.now(timezone.utc); stamp, day = now.strftime("%Y-%m-%dT%H:%M:%SZ"), now.strftime("%Y-%m-%d")
    sm = get("https://www.dm.at/product-sitemap.xml", raw=True)[0].decode()
    urls = sorted(set(u for u in re.findall(r"https://www\.dm\.at/p/d/\d+/[a-z0-9-]+", sm) if SLUG.search(u.rsplit("/", 1)[1]) and not SLUG_NOT.search(u.rsplit("/", 1)[1])))
    print("sitemap candidates", len(urls))
    probed, rows = [], []
    for u in urls:
        dan = int(re.search(r"/p/d/(\d+)/", u).group(1))
        try: d = get(API.format(dan=dan))
        except Exception as e:
            probed.append(dict(dan=dan, url=u, error=str(e)[:80])); time.sleep(1); continue
        time.sleep(1.0)
        crumbs = d.get("breadcrumbs") or []
        brand = (d.get("brand") or {}).get("name") or ""
        title = (d.get("title") or {}).get("headline") or ""
        rec = dict(dan=dan, url=u, api=API.format(dan=dan), brand=brand, title=title, breadcrumbs=crumbs, gtin=d.get("gtin"),
                   price=(((d.get("price") or {}).get("price") or {}).get("current") or {}).get("value"))
        if tuple(crumbs[:2]) != KEEP_CRUMB or (len(crumbs) > 2 and crumbs[2] in DROP_SUB) or DROP_NAME.search(title):
            probed.append(dict(rec, decision="skip: not a ready meal per dm breadcrumb")); continue
        nut, basis = nutrition(d)
        price = num(rec["price"])
        imgs = [i["src"] for i in d.get("images") or [] if i.get("src") and not i.get("isAiGenerated")]
        img, vinfo = None, None
        if imgs:
            ok, ct, n = verify(imgs[0]); vinfo = dict(verified=ok, content_type=ct, bytes=n); img = imgs[0] if ok else None
            time.sleep(0.5)
        clean = re.sub(r",\s*\d+(?:,\d+)?\s*(g|kg|ml|l)\s*$", "", title, flags=re.I).strip()
        brand_disp = {"TRESSBRÜDER": "Tressbrüder"}.get(brand, brand)
        row = dict(name=f"{brand_disp} {clean}".strip(), brand=brand_disp, store="dm", price_eur=price, size_g=size_g(title, d.get("a11yLabel")),
                   **{k: nut.get(k) for k in ("kcal_100", "protein_100", "fat_100", "satfat_100", "carbs_100", "sugar_100", "fiber_100", "salt_100")},
                   url=u, ean=d.get("gtin"), price_source=f"dm.at live {day} (products.dm.de product JSON)", image_url=img,
                   category=" > ".join(crumbs[1:]), ingredients=texts(d, "Zutaten") or None, origin=texts(d, "Hergestellt in"),
                   manufacturer=(texts(d, "Anschrift des Unternehmens") or "").split("\n")[0] or None,
                   prep_hint=texts(d, "Verwendungshinweise"), nutrition_basis=basis, dm_dan=dan)
        if not row["ingredients"]:
            row["ingredients"] = next((t.split("Zutaten:", 1)[1].strip()[:1500] for b in d.get("descriptionGroups") or [] for c in (b.get("contentBlock") or []) for t in (c.get("texts") or []) if "Zutaten:" in t), None)
        macros = [row[k] for k in ("protein_100", "fat_100", "carbs_100")]
        if row["kcal_100"] and all(v == 0 for v in macros if v is not None):
            # dm table is a placeholder (e.g. 117 kcal but 0 g fat/carbs/protein) -> keep nothing we cannot trust
            for k in ("protein_100", "fat_100", "satfat_100", "carbs_100", "sugar_100", "fiber_100", "salt_100"): row[k] = None
            row["nutrition_note"] = "dm.at Nährwerttabelle unplausibel (alle Makros 0 g) – Makros nicht übernommen"
        if re.search(r"tasse|trockenmischung|instant|fasten", title, re.I):
            row["nutrition_note"] = f"Instant/Trockenmischung: dm-Nährwertbasis '{basis}' (zubereitet bzw. unklar); Packungsgröße = Trockengewicht"
        if price is None or row["kcal_100"] is None:
            probed.append(dict(rec, decision="skip: no price or nutrition in dm JSON")); continue
        probed.append(dict(rec, decision="keep", image=vinfo, nutrition_basis=basis))
        rows.append(row)
    # merge into fertig/dm_live.json by DAN (existing names kept so score.py keys stay stable)
    path = os.path.join(FERTIG, "dm_live.json"); live = json.load(open(path))
    dan_of = lambda x: int(m.group(1)) if (m := re.search(r"/p/d/(\d+)/", x.get("url") or "")) else None
    by = {dan_of(x): x for x in live}
    added, updated = [], []
    for r in rows:
        x = by.get(r["dm_dan"])
        if x:
            for k, v in r.items():
                if k == "name" or v is None: continue
                x[k] = v
            updated.append(x["name"])
        else:
            live.append(r); added.append(r["name"])
    json.dump(live, open(path, "w"), ensure_ascii=False, indent=1)
    # heisse-preise Altpreis rows (no url) that are the same dm product as a live row -> exclude duplicate
    # match against score.py *source* files (scored.json already has previous excludes applied)
    sc = []
    for f in ("expand.json", "classics.json", "classics_ext.json", "brandfam_products.json", "connectors_new.json", "expand_v5.json", "other.json", "more_meals_norm.json"):
        try: d = json.load(open(os.path.join(FERTIG, f)))
        except Exception: continue
        sc += d if isinstance(d, list) else d.get("products", [])
    norm = lambda s: re.sub(r"[^a-z0-9]", "", (s or "").lower().replace("ß", "ss").replace("&", "und"))
    keyset = {norm(f"{p['brand']} {p['title']}"): p for p in probed if p.get("decision") == "keep"}
    fixes = []
    for x in sc:
        if (x.get("store") or "").lower() != "dm" or x.get("url") or "heisse-preise" not in (x.get("price_source") or ""): continue
        p = keyset.get(norm(x["name"]))
        if p and not any(f["name"] == x["name"] for f in fixes):
            fixes.append(dict(name=x["name"], field="exclude", new="__exclude__",
                              reason=f"Duplikat: gleiches dm-Produkt live auf dm.at (DAN {p['dan']}, {p['price']}, {day}); heisse-preise Altpreis-Zeile ersetzt"))
    for r in rows:
        if (r.get("nutrition_note") or "").startswith("Instant/Trockenmischung"):
            fixes.append(dict(url=r["url"], name=r["name"], field="dry", new=True,
                              reason="Instant/Trockenmischung: dm-Nährwerte beziehen sich auf zubereitetes Produkt, Packung = Trockengewicht -> nicht in Rankings"))
    in_sitemap = {norm(f"{p['brand']} {p['title']}") for p in probed}
    delisted = [x["name"] for x in sc if (x.get("store") or "").lower() == "dm" and not x.get("url") and "heisse-preise" in (x.get("price_source") or "") and norm(x["name"]) not in in_sitemap]
    os.makedirs(os.path.join(FERTIG, "qa"), exist_ok=True)
    json.dump(fixes, open(os.path.join(FERTIG, "qa", "dm_live_fixes.json"), "w"), ensure_ascii=False, indent=1)
    ev = dict(fetched_at=stamp, sources=["https://www.dm.at/product-sitemap.xml", API], sitemap_candidates=len(urls),
              probed=probed, kept=len(rows), added=added, updated=updated, heisse_duplicates_excluded=[f["name"] for f in fixes],
              heisse_rows_not_in_dm_sitemap=delisted,
              note="heisse_rows_not_in_dm_sitemap: no dm.at product page in the 2026 product sitemap -> no live price possible; kept as flagged Altpreis rows")
    json.dump(ev, open(os.path.join(RAW, f"dm_live_{day}.json"), "w"), ensure_ascii=False, indent=1)
    print(f"kept {len(rows)} · added {len(added)} · updated {len(updated)} · heisse dups excluded {len(fixes)} · delisted {len(delisted)}")
    for a in added: print("  +", a)
    for n_ in delisted: print("  delisted:", n_)

if __name__ == "__main__":
    main()
