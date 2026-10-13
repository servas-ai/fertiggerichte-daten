"""Enrich Hofer ready-meal rows that lack image_url; refresh Hofer prices from heisse-preise.

Photos (strict match only, never fabricate):
  - Open Food Facts: local pool raw/off_hofer_pool_*.json + fertig/off_hofer.json
    + data/off_ready_meals_at.csv (+ optional live API refresh)
  - Aldi CDN titles from /workspace/fertig/brandfam/hofer_raw.json
    (only dm.emea.cms.aldi.cx URLs that HEAD as image/* and size >500;
     upgrade scaleWidth/232 → 400 when that HEAD-oks)

Matching requires brand-family overlap AND substantial name-token overlap
(dish-type must agree; no substring-only false friends).

Prices:
  - Exact name match to heisse-preise store=hofer
  - Latest priceHistory date/price → update fetched_at / price_source / price_eur
  - Status: 2026 → live 2026; 2025 → Preis 2025; older → keep historic label
  - Never invent live 2026 without a 2026 date (heisse Hofer has no 2026 as of 2026-10-13)

Writes:
  - raw/hofer_images_YYYY-MM-DD.json
  - raw/hofer_prices_YYYY-MM-DD.json
  - data/products.{csv,json} image_url for verified matches
  - data/prices.{csv,json} for refreshed rows
  - optional --patch-app fertig-app/public/data.json (img / price fields)
  - optional --patch-sources fertig JSON lists

Rate: ≥0.7 s between HEAD/API calls. hofer.at is Akamai-blocked — do not scrape it.
"""
from __future__ import annotations
import argparse, csv, json, os, re, sys, time, unicodedata, urllib.parse, urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(ROOT, "raw")
UA = "ServasFoodResearch/1.0 (fertig@servas.ai)"
OFF_UA = UA
ALDI_HOST = "dm.emea.cms.aldi.cx"
HEISSE_HOFER_CACHE = "/tmp/heisse_hofer.json"
HP_PATH = "/workspace/hp.json.gz"

BRAND_ALIASES = {
    "good choice": "good choice",
    "goodchoice": "good choice",
    "primana": "primana",
    "cucina nobile": "cucina nobile",
    "cucina": "cucina",
    "fairhof": "fairhof",
    "golden seafood": "golden seafood",
    "le gusto": "le gusto",
    "legusto": "le gusto",
    "zurück zum ursprung": "zurück zum ursprung",
    "zuruck zum ursprung": "zurück zum ursprung",
    "asia green garden": "asia green garden",
    "green garden": "asia green garden",
    "nature's gold": "nature's gold",
    "natures gold": "nature's gold",
    "my best veggie": "my best veggie",
    "hofer gourmet": "hofer gourmet",
    "mamia": "mamia",
    "bio mamia": "mamia",
    "pik.": "pik",
    "pik": "pik",
    "original greisinger": "greisinger",
    "greisinger": "greisinger",
    "wonnemeyer": "wonnemeyer",
    "hütthaler": "hütthaler",
    "hutthaler": "hütthaler",
    "landgut": "landgut",
    "rettenwert": "rettenwert",
    "iglo": "iglo",
}

DISH = {
    "spaghetti", "spaghettini", "penne", "lasagne", "lasagna", "gnocchi", "gnocchie",
    "risotto", "pizza", "steinofenpizza", "wrap", "wraps", "curry", "suppe", "eintopf",
    "gulasch", "cevapcici", "schnitzel", "nuggets", "knodel", "knoedel", "spaetzle",
    "spatzle", "ravioli", "tortellini", "tortelloni", "carbonara", "bolognese", "nudeln",
    "pasta", "burger", "salat", "poke", "bowl", "ribs", "spareribs", "geschnetzeltes",
    "braten", "groestl", "cannelloni", "schupfnudeln", "polenta", "hotdog",
}

# Modifiers that must agree when present on the product side
MODIFIERS = {
    "spinat", "natur", "fleisch", "gemuese", "mediterran", "pikant",
    "kuerbiskern", "tomate", "mozzarella", "ricotta", "pilz", "pilze", "lachs",
    "thunfisch", "suess", "sauer", "indisch",
}

STOP = {
    "und", "mit", "der", "die", "das", "fuer", "fur", "aus", "von", "den", "dem",
    "ein", "eine", "einer", "eines", "oder", "per", "the", "and", "for", "bio",
    "hofer", "aldi", "fertiggericht", "fertiggerichte", "italienische", "tk", "xxl",
    "art", "classic", "classico", "premium", "family", "familia", "mobile", "nobile", "basis",
}

SYNONYMS = {
    "chicken": "huhn", "huhn": "huhn", "huehner": "huhn", "haehnchen": "huhn",
    "huehnerfiletstreifen": "huehnerfiletstreifen",
    "knoedel": "knoedel", "knodel": "knoedel",
    "spaetzle": "spaetzle", "spatzle": "spaetzle",
    "lasagneblaetter": "lasagneblaetter",
    "suess": "suess", "sauer": "sauer",
}


def fold(s: str) -> str:
    s = (s or "").lower()
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s


def brand_family(brand: str, name: str = "") -> str | None:
    text = fold(f"{brand} {name}")
    for alias in sorted(BRAND_ALIASES.keys(), key=len, reverse=True):
        if fold(alias) in text:
            if alias == "cucina" and "cucina nobile" in text:
                return "cucina nobile"
            return BRAND_ALIASES[alias]
    return None


BRAND_TOKS: set[str] = set()
for _a in BRAND_ALIASES:
    BRAND_TOKS.update(re.findall(r"[a-z0-9]{3,}", fold(_a)))


def raw_tokens(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]{3,}", fold(s)) if t not in STOP]


def canon_tok(t: str) -> str:
    return SYNONYMS.get(t, t)


def name_tokens(s: str, brand: str | None = None) -> list[str]:
    toks = [canon_tok(t) for t in raw_tokens(s)]
    drop = set(BRAND_TOKS)
    bf = brand_family(brand or "", s)
    if bf:
        drop.update(re.findall(r"[a-z0-9]{3,}", fold(bf)))
    # drop leftover brand fragments + bare size tokens (400g, 1kg, etc.)
    drop |= {"good", "choice", "golden", "seafood", "asia", "green", "garden", "zum", "ursprung", "zurueck"}
    out = []
    for t in toks:
        if t in drop:
            continue
        if re.fullmatch(r'\d+g', t) or re.fullmatch(r'\d+kg', t) or re.fullmatch(r'\d+ml', t):
            continue
        out.append(t)
    return out


def size_hint(s: str) -> int | None:
    m = re.search(r"(\d+[.,]?\d*)\s*(kg|g)\b", (s or "").lower().replace(",", "."))
    if not m:
        return None
    n = float(m.group(1))
    return int(n * 1000) if m.group(2) == "kg" else int(n)


def dish_tokens(toks: list[str]) -> set[str]:
    return set(toks) & DISH


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", fold(s))


def head(url: str):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, (r.headers.get("content-type") or ""), int(r.headers.get("content-length") or 0)
    except Exception as e:
        return 0, type(e).__name__ + ":" + str(e)[:80], 0


def match_detail(prod_name, prod_brand, cand_name, cand_brand, cand_qty=""):
    bf_p = brand_family(prod_brand, prod_name)
    bf_c = brand_family(cand_brand, cand_name)
    if not bf_p or not bf_c:
        return None
    if not (bf_p == bf_c or {bf_p, bf_c} <= {"cucina", "cucina nobile"}):
        return None
    pt = name_tokens(prod_name, prod_brand)
    ct = name_tokens(cand_name, cand_brand)
    if not pt or not ct:
        return None
    inter = set(pt) & set(ct)
    if not inter:
        return None
    pd, cd = dish_tokens(pt), dish_tokens(ct)
    if pd and not (pd & cd):
        return None
    p_dist = set(t for t in pt if t not in DISH)
    c_dist = set(t for t in ct if t not in DISH)
    dist_inter = p_dist & c_dist
    strong_dist = [t for t in dist_inter if len(t) >= 5]
    very_strong = [t for t in dist_inter if len(t) >= 8]
    subset = set(pt).issubset(set(ct)) or set(ct).issubset(set(pt))

    # Product modifiers must appear on candidate when product has them
    p_mods = set(pt) & MODIFIERS
    if p_mods and not (p_mods & set(ct)):
        # allow if dish+strong other overlap is very strong (e.g. full name subset without size)
        if not (subset and len(inter) >= 2 and (pd & cd)):
            return None

    ok = False
    if len(inter) >= 2 and ((pd & cd) or strong_dist):
        ok = True
    elif subset and len(pt) >= 2 and len(inter) >= 2:
        ok = True
    elif very_strong and (not pd or (pd & cd)):
        ok = True
    elif len(inter) >= 3:
        ok = True
    if not ok:
        return None
    if p_dist and c_dist and not dist_inter:
        if inter <= DISH and len(inter) >= 2:
            pass
        else:
            return None

    score = len(inter) * 3 + len(strong_dist) * 4 + len(pd & cd) * 2
    if subset:
        score += 5
    if p_mods & set(ct):
        score += 3 * len(p_mods & set(ct))
    psz = size_hint(prod_name)
    csz = size_hint(cand_qty) or size_hint(cand_name)
    if psz and csz:
        if psz == csz:
            score += 4
        elif abs(psz - csz) > max(50, psz * 0.2):
            score -= 3
    ratio = len(inter) / max(1, min(len(set(pt)), len(set(ct))))
    if ratio < 0.5 and not very_strong and not (subset and len(inter) >= 2):
        return None
    if score < 8:
        return None
    # Extra false-friend guards
    joined_p = " ".join(pt)
    joined_c = " ".join(ct)
    if "suess" in pt and "suess" not in ct:
        return None
    if "sauer" in pt and "sauer" not in ct:
        return None
    if "mini" in ct and "mini" not in pt:
        return None
    if inter <= {"box", "party", "snack"}:
        return None
    return {
        "score": score,
        "inter": sorted(inter),
        "ratio": round(ratio, 3),
        "dish": sorted(pd & cd),
        "dist": sorted(dist_inter),
        "pt": pt,
        "ct": ct,
    }


def load_off_pool(extra_paths: list[str]) -> list[dict]:
    rows = []
    paths = list(extra_paths)
    # newest pool in raw/
    for fn in sorted(os.listdir(RAW)) if os.path.isdir(RAW) else []:
        if fn.startswith("off_hofer_pool_") and fn.endswith(".json"):
            paths.append(os.path.join(RAW, fn))
    for p in (
        "/workspace/fertig/off_hofer.json",
        os.path.join(DATA, "off_ready_meals_at.csv"),
    ):
        paths.append(p)
    seen = set()
    for path in paths:
        if not path or not os.path.exists(path) or path in seen:
            continue
        seen.add(path)
        if path.endswith(".csv"):
            for r in csv.DictReader(open(path)):
                rows.append({
                    "code": r.get("ean"),
                    "product_name": r.get("name"),
                    "brands": r.get("brand"),
                    "image_front_url": r.get("image_url"),
                    "quantity": f"{r['size_g']} g" if r.get("size_g") else "",
                    "_src": path,
                })
            continue
        try:
            d = json.load(open(path))
        except Exception:
            continue
        if isinstance(d, list):
            for p in d:
                p = dict(p)
                p["_src"] = path
                rows.append(p)
        elif isinstance(d, dict) and "products" in d:
            for p in d["products"]:
                p = dict(p)
                p["_src"] = path
                rows.append(p)
    by = {}
    for p in rows:
        c = str(p.get("code") or "").strip()
        if not c:
            continue
        img = p.get("image_front_url") or p.get("image_url") or ""
        old = by.get(c)
        if not old or (img and not (old.get("image_front_url") or old.get("image_url"))):
            by[c] = p
    return list(by.values())


def load_brandfam(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    raw = json.load(open(path))
    out = []
    for slug, v in raw.items():
        txt = v.get("txt") or []
        title = ""
        for t in txt:
            m = re.search(r'title="([^"]+)"', t)
            if m:
                title = m.group(1)
                break
        q = v.get("q") or ""
        joined = " ".join(txt)
        brand = q
        for t in txt:
            if t.upper() in {
                "GOOD CHOICE", "PRIMANA", "CUCINA", "CUCINA NOBILE",
                "ASIA GREEN GARDEN", "NATURE'S GOLD", "LE GUSTO",
                "ZURÜCK ZUM URSPRUNG", "GOURMET", "FAIRHOF", "GOLDEN SEAFOOD",
            }:
                brand = t
                break
        img = v.get("img") or ""
        if ALDI_HOST not in img:
            continue
        out.append({
            "title": title,
            "brands": brand,
            "q": q,
            "img": img,
            "price": v.get("price"),
            "path": slug,
            "joined": joined,
        })
    return out


def upgrade_aldi(url: str) -> str:
    return re.sub(r"scaleWidth/232", "scaleWidth/400", url)


def load_heisse_hofer():
    if os.path.exists(HEISSE_HOFER_CACHE):
        return json.load(open(HEISSE_HOFER_CACHE))
    path = HP_PATH if os.path.exists(HP_PATH) else None
    if not path:
        sys.path.insert(0, "/workspace/food-connectors")
        from food_connectors.adapters.heisse import data as heisse_data
        rows = [x for x in heisse_data() if x.get("store") == "hofer"]
    else:
        data = json.load(open(path))
        rows = [x for x in data if x.get("store") == "hofer"]
    json.dump(rows, open(HEISSE_HOFER_CACHE, "w"), ensure_ascii=False)
    return rows


def write_csv_json(name: str, rows: list[dict]):
    if not rows:
        return
    fields = list(rows[0].keys())
    with open(os.path.join(DATA, f"{name}.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    json.dump(rows, open(os.path.join(DATA, f"{name}.json"), "w"), ensure_ascii=False, indent=1)


def patch_app(path, img_by_pid, img_by_norm, price_by_pid):
    import hashlib
    d = json.load(open(path))
    n_img = n_price = 0
    for r in d.get("rows") or []:
        if r.get("store") != "Hofer":
            continue
        pid = hashlib.sha1(((r.get("url") or "") + "|" + r["name"] + "|" + r["store"]).encode()).hexdigest()[:12]
        if not r.get("img"):
            url = img_by_pid.get(pid) or img_by_norm.get(norm(r["name"]))
            if url:
                r["img"] = url
                n_img += 1
        if pid in price_by_pid:
            pr = price_by_pid[pid]
            if pr.get("price_eur") is not None:
                try:
                    r["price"] = float(pr["price_eur"])
                except Exception:
                    pass
            if pr.get("price_status"):
                r["pstat"] = pr["price_status"]
            if pr.get("price_source"):
                r["psrc"] = pr["price_source"]
            n_price += 1
    if n_img or n_price:
        json.dump(d, open(path, "w"), ensure_ascii=False, indent=None, separators=(",", ":"))
    return n_img, n_price


def patch_list_json(path, updates_by_norm_name):
    if not os.path.exists(path):
        return 0
    rows = json.load(open(path))
    n = 0
    for r in rows:
        store = (r.get("store") or "")
        if not (store.upper().startswith("HOFER") or store == "Hofer"):
            continue
        key = norm(r.get("name") or "")
        if key in updates_by_norm_name and not (r.get("image_url") or r.get("img") or "").strip():
            r["image_url"] = updates_by_norm_name[key]
            n += 1
    if n:
        json.dump(rows, open(path, "w"), ensure_ascii=False, indent=2)
    return n


def status_for_date(date: str, old_status: str) -> str:
    if not date:
        return old_status
    y = date[:4]
    if y == "2026":
        return "live 2026"
    if y == "2025":
        return "Preis 2025"
    # older: keep historic label (do not invent 2025/2026)
    if old_status in ("live 2026", "Preis 2025"):
        return f"Preis {y}" if y.isdigit() else old_status
    return old_status or f"Preis {y}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=0, help="max HEAD checks (0=all)")
    ap.add_argument("--patch-app", default="")
    ap.add_argument("--patch-sources", action="store_true")
    ap.add_argument("--skip-prices", action="store_true")
    ap.add_argument("--skip-images", action="store_true")
    ap.add_argument("--brandfam", default="/workspace/fertig/brandfam/hofer_raw.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    products = list(csv.DictReader(open(os.path.join(DATA, "products.csv"))))
    prices = list(csv.DictReader(open(os.path.join(DATA, "prices.csv"))))
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(RAW, exist_ok=True)

    img_by_pid = {}
    img_by_norm = {}
    img_evidence = {
        "fetched_at": now,
        "method": "strict OFF brand+token match + Aldi CDN brandfam title match; HEAD verify",
        "matches": [],
        "unmatched": [],
        "failed_head": [],
        "summary": {},
    }

    if not args.skip_images:
        hofer_no = [r for r in products if r["chain"] == "Hofer" and not (r.get("image_url") or "").strip()]
        pool = load_off_pool([])
        off_by = defaultdict(list)
        for p in pool:
            img = p.get("image_front_url") or p.get("image_url") or ""
            if not img:
                continue
            bf = brand_family(p.get("brands") or "", p.get("product_name") or "")
            if bf:
                off_by[bf].append(p)
        brandfam = load_brandfam(args.brandfam)
        print(f"hofer without photo: {len(hofer_no)}; OFF pool imgs by brand: "
              f"{ {k: len(v) for k, v in sorted(off_by.items(), key=lambda x: -len(x[1]))} }; "
              f"brandfam aldi: {len(brandfam)}")

        pending = []  # (product, url, meta)
        for r in hofer_no:
            bf = brand_family(r.get("brand") or "", r.get("name") or "")
            best = None
            best_d = None
            best_src = None
            if bf:
                cands = list(off_by.get(bf, []))
                if bf in ("cucina", "cucina nobile"):
                    cands = cands + off_by.get("cucina", []) + off_by.get("cucina nobile", [])
                # dedupe by code
                seen_c = set()
                uniq = []
                for c in cands:
                    code = c.get("code")
                    if code in seen_c:
                        continue
                    seen_c.add(code)
                    uniq.append(c)
                for c in uniq:
                    d = match_detail(
                        r["name"], r.get("brand"),
                        c.get("product_name") or "", c.get("brands") or "",
                        c.get("quantity") or "",
                    )
                    if not d:
                        continue
                    if not best or d["score"] > best_d["score"]:
                        best, best_d, best_src = c, d, "off"
            # brandfam near-exact / strict match if no OFF or as alternative if higher score
            for c in brandfam:
                d = match_detail(
                    r["name"], r.get("brand") or c.get("brands"),
                    c.get("title") or "", c.get("brands") or c.get("q") or "",
                )
                if not d:
                    continue
                if not best or d["score"] > best_d["score"]:
                    best, best_d, best_src = c, d, "aldi_cdn"

            if not best:
                img_evidence["unmatched"].append({
                    "product_id": r["product_id"], "name": r["name"], "brand": r.get("brand"),
                    "reason": "no_strict_match",
                })
                continue

            if best_src == "off":
                url = best.get("image_front_url") or best.get("image_url")
                meta = {
                    "product_id": r["product_id"], "name": r["name"], "brand": r.get("brand"),
                    "source": "openfoodfacts",
                    "off_code": best.get("code"),
                    "off_name": best.get("product_name"),
                    "off_brands": best.get("brands"),
                    "image_url": url,
                    "match": best_d,
                }
            else:
                url = upgrade_aldi(best["img"])
                meta = {
                    "product_id": r["product_id"], "name": r["name"], "brand": r.get("brand"),
                    "source": "aldi_cdn_brandfam",
                    "title": best.get("title"),
                    "brandfam_path": best.get("path"),
                    "image_url": url,
                    "image_url_orig": best.get("img"),
                    "match": best_d,
                }
            pending.append((r, url, meta))

        checked = 0
        for r, url, meta in pending:
            if args.limit and checked >= args.limit:
                img_evidence["unmatched"].append({
                    "product_id": r["product_id"], "name": r["name"], "reason": "limit_skipped",
                })
                continue
            # try upgraded URL first; fall back to original for aldi
            urls_try = [url]
            if meta.get("image_url_orig") and meta["image_url_orig"] != url:
                urls_try.append(meta["image_url_orig"])
            ok_url = None
            head_info = None
            for u in urls_try:
                st, ctype, clen = head(u)
                checked += 1
                time.sleep(args.delay)
                head_info = (st, ctype, clen, u)
                if st == 200 and ctype.startswith("image/") and clen > 500:
                    ok_url = u
                    break
                # OFF sometimes omits content-length on HEAD; accept image/* with 200 even if clen=0
                if st == 200 and ctype.startswith("image/") and "openfoodfacts.org" in u:
                    ok_url = u
                    break
            if ok_url:
                img_by_pid[r["product_id"]] = ok_url
                img_by_norm[norm(r["name"])] = ok_url
                meta["image_url"] = ok_url
                meta["bytes"] = head_info[2]
                meta["content_type"] = head_info[1]
                img_evidence["matches"].append(meta)
            else:
                meta["status"] = head_info[0] if head_info else 0
                meta["content_type"] = head_info[1] if head_info else ""
                meta["bytes"] = head_info[2] if head_info else 0
                meta["tried"] = urls_try
                img_evidence["failed_head"].append(meta)
            if checked % 20 == 0:
                print(f"  HEAD checked {checked}: ok={len(img_evidence['matches'])} fail={len(img_evidence['failed_head'])}")

        img_evidence["summary"] = {
            "missing_before": len(hofer_no),
            "candidates": len(pending),
            "checked": checked,
            "matched_ok": len(img_evidence["matches"]),
            "failed_head": len(img_evidence["failed_head"]),
            "unmatched": len(img_evidence["unmatched"]),
        }
        print("images summary", img_evidence["summary"])

    # --- prices ---
    price_evidence = {
        "fetched_at": now,
        "method": "heisse-preise.io store=hofer exact name match → latest priceHistory",
        "updates": [],
        "unmatched": [],
        "summary": {},
    }
    price_by_pid = {}
    if not args.skip_prices:
        heisse = load_heisse_hofer()
        by_h = defaultdict(list)
        for x in heisse:
            by_h[norm(x.get("name") or "")].append(x)
        hofer_prices = [r for r in prices if r["chain"] == "Hofer"]
        prod_by_id = {p["product_id"]: p for p in products if p["chain"] == "Hofer"}
        print(f"hofer price rows: {len(hofer_prices)}; heisse hofer: {len(heisse)}")
        for r in hofer_prices:
            p = prod_by_id.get(r["product_id"])
            if not p:
                price_evidence["unmatched"].append({"product_id": r["product_id"], "reason": "no_product"})
                continue
            xs = by_h.get(norm(p["name"])) or []
            if not xs:
                price_evidence["unmatched"].append({
                    "product_id": r["product_id"], "name": p["name"], "reason": "no_heisse_exact_name",
                })
                continue
            best_date = ""
            best_price = None
            for x in xs:
                for ph in (x.get("priceHistory") or []):
                    d = ph.get("date") or ""
                    if d >= best_date:
                        best_date = d
                        best_price = ph.get("price")
            if not best_date:
                price_evidence["unmatched"].append({
                    "product_id": r["product_id"], "name": p["name"], "reason": "no_priceHistory",
                })
                continue
            new_status = status_for_date(best_date, r.get("price_status") or "")
            new_src = f"heisse-preise.io hofer (Preisstand {best_date})"
            if best_date.startswith("2026"):
                new_src += " – live 2026"
            elif best_date.startswith("2025"):
                new_src += " – Altpreis 2025, nicht live 2026 (hofer.at Akamai-blocked)"
            else:
                new_src += f" – historisch {best_date[:4]}"
            changed = (
                (r.get("fetched_at") or "") != best_date
                or (best_price is not None and str(r.get("price_eur")) != str(best_price))
                or r.get("price_status") != new_status
                or (r.get("price_source") or "") != new_src
            )
            if not changed:
                continue
            upd = {
                "product_id": r["product_id"],
                "name": p["name"],
                "old_price": r.get("price_eur"),
                "new_price": best_price if best_price is not None else r.get("price_eur"),
                "old_fetched_at": r.get("fetched_at"),
                "new_fetched_at": best_date,
                "old_status": r.get("price_status"),
                "new_status": new_status,
                "price_source": new_src,
            }
            price_evidence["updates"].append(upd)
            price_by_pid[r["product_id"]] = {
                "price_eur": upd["new_price"],
                "price_status": new_status,
                "fetched_at": best_date,
                "price_source": new_src,
            }
        price_evidence["summary"] = {
            "price_rows": len(hofer_prices),
            "updated": len(price_evidence["updates"]),
            "unmatched": len(price_evidence["unmatched"]),
            "by_new_status": dict(Counter(u["new_status"] for u in price_evidence["updates"])),
        }
        print("prices summary", price_evidence["summary"])

    if args.dry_run:
        print("dry-run, not writing")
        return

    img_path = os.path.join(RAW, f"hofer_images_{day}.json")
    price_path = os.path.join(RAW, f"hofer_prices_{day}.json")
    if not args.skip_images:
        json.dump(img_evidence, open(img_path, "w"), ensure_ascii=False, indent=2)
        print("wrote", img_path)
        for r in products:
            if r["product_id"] in img_by_pid:
                r["image_url"] = img_by_pid[r["product_id"]]
        write_csv_json("products", products)
        print("updated data/products.*", len(img_by_pid), "images")
        # Overlay for fertig/score.py rebuilds (mirrors spar_cdn_overlay.json)
        ov = {
            "fetched_at": now,
            "method": "strict OFF/Aldi match; HEAD-verified",
            "images": [{"name": m["name"], "image_url": m["image_url"], "product_id": m["product_id"],
                        "off_code": m.get("off_code")} for m in img_evidence["matches"]],
        }
        ov_raw = os.path.join(RAW, "hofer_images_overlay.json")
        json.dump(ov, open(ov_raw, "w"), ensure_ascii=False, indent=2)
        fertig_ov = "/workspace/fertig/hofer_images_overlay.json"
        try:
            json.dump(ov, open(fertig_ov, "w"), ensure_ascii=False, indent=2)
            print("wrote overlay", ov_raw, "and", fertig_ov)
        except Exception as e:
            print("overlay fertig write skipped", e)

    if not args.skip_prices and price_by_pid:
        json.dump(price_evidence, open(price_path, "w"), ensure_ascii=False, indent=2)
        print("wrote", price_path)
        for r in prices:
            if r["product_id"] in price_by_pid:
                pr = price_by_pid[r["product_id"]]
                r["price_eur"] = pr["price_eur"]
                r["price_status"] = pr["price_status"]
                r["fetched_at"] = pr["fetched_at"]
                r["price_source"] = pr["price_source"]
        write_csv_json("prices", prices)
        print("updated data/prices.*", len(price_by_pid), "rows")
    elif not args.skip_prices:
        json.dump(price_evidence, open(price_path, "w"), ensure_ascii=False, indent=2)
        print("wrote", price_path, "(no row updates)")

    if args.patch_app:
        n_img, n_price = patch_app(args.patch_app, img_by_pid, img_by_norm, price_by_pid)
        print("patched app data.json img=", n_img, "price=", n_price)

    if args.patch_sources and img_by_norm:
        for p in (
            "/workspace/fertig/expand.json",
            "/workspace/fertig/brandfam_products.json",
            "/workspace/fertig/classics_ext.json",
        ):
            n = patch_list_json(p, img_by_norm)
            print("patched", p, n)


if __name__ == "__main__":
    main()
