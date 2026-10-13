"""Enrich Spar ready-meal rows that lack image_url.

Match each Spar product name to heisse-preise.io (store=spar), build the public
CDN URL from the article id, HEAD-verify it returns image/jpeg, then write:

  - raw/spar_cdn_images_YYYY-MM-DD.json  (evidence)
  - data/products.{csv,json}             (image_url filled)
  - optional --patch-app path to fertig-app/public/data.json (img field)
  - optional --patch-sources fertig expand.json / brandfam_products.json / classics_ext.json

Never fabricates: only verified HEAD 200 + image/* URLs are kept.
Rate: ≥0.6 s between HEAD requests. robots/ToS: CDN is public product imagery.
"""
from __future__ import annotations
import argparse, csv, json, os, re, sys, time, urllib.request
from datetime import datetime, timezone
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(ROOT, "raw")
sys.path.insert(0, "/workspace/food-connectors")
from food_connectors.adapters.heisse import data as heisse_data  # noqa: E402

CDN = "https://cdn1.interspar.at/cachableservlets/articleImage.dam/at/{aid}/dt_main.jpg"
UA = "FertiggerichteBot/1.0 (servas.ai research; +https://github.com/servas-ai/fertiggerichte-daten)"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def head(url: str):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, (r.headers.get("content-type") or ""), int(r.headers.get("content-length") or 0)
    except Exception as e:
        return 0, type(e).__name__ + ":" + str(e)[:60], 0


def load_heisse_spar():
    by = {}
    for x in heisse_data():
        if x.get("store") != "spar":
            continue
        by.setdefault(norm(x.get("name") or ""), []).append(x)
    return by


def write_products(rows):
    fields = list(rows[0].keys())
    with open(os.path.join(DATA, "products.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    json.dump(rows, open(os.path.join(DATA, "products.json"), "w"), ensure_ascii=False, indent=1)


def patch_list_json(path, updates_by_norm_name):
    """Patch image_url on list-of-dict JSONs where store==Spar and name matches."""
    if not os.path.exists(path):
        return 0
    rows = json.load(open(path))
    n = 0
    for r in rows:
        if (r.get("store") or "").upper().startswith("SPAR") or r.get("store") == "Spar":
            key = norm(r.get("name") or "")
            if key in updates_by_norm_name and not (r.get("image_url") or "").strip():
                r["image_url"] = updates_by_norm_name[key]
                n += 1
    if n:
        json.dump(rows, open(path, "w"), ensure_ascii=False, indent=2)
        if not path.endswith(".json"):
            pass
    return n


def patch_app(path, updates_by_pid, updates_by_norm):
    import hashlib
    d = json.load(open(path))
    n = 0
    for r in d.get("rows") or []:
        if r.get("store") != "Spar":
            continue
        if r.get("img"):
            continue
        pid = hashlib.sha1(((r.get("url") or "") + "|" + r["name"] + "|" + r["store"]).encode()).hexdigest()[:12]
        url = updates_by_pid.get(pid) or updates_by_norm.get(norm(r["name"]))
        if url:
            r["img"] = url
            n += 1
    if n:
        json.dump(d, open(path, "w"), ensure_ascii=False, indent=None, separators=(",", ":"))
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=float, default=0.7)
    ap.add_argument("--limit", type=int, default=0, help="max HEAD checks (0=all)")
    ap.add_argument("--patch-app", default="")
    ap.add_argument("--patch-sources", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    products = list(csv.DictReader(open(os.path.join(DATA, "products.csv"))))
    spar_no = [r for r in products if r["chain"] == "Spar" and not (r.get("image_url") or "").strip()]
    by = load_heisse_spar()
    print(f"spar without photo: {len(spar_no)}; heisse spar name keys: {len(by)}")

    evidence = {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": "heisse-preise spar id → cdn1.interspar.at articleImage HEAD verify",
        "matches": [],
        "unmatched": [],
        "failed_head": [],
    }
    updates_by_pid = {}
    updates_by_norm = {}
    checked = 0
    for r in spar_no:
        xs = by.get(norm(r["name"])) or []
        if not xs:
            evidence["unmatched"].append({"product_id": r["product_id"], "name": r["name"]})
            continue
        # prefer id that looks like article number already used in existing CDN URLs
        aid = str(xs[0]["id"])
        url = CDN.format(aid=aid)
        if args.limit and checked >= args.limit:
            break
        st, ctype, clen = head(url)
        checked += 1
        time.sleep(args.delay)
        if st == 200 and ctype.startswith("image/") and clen > 500:
            updates_by_pid[r["product_id"]] = url
            updates_by_norm[norm(r["name"])] = url
            evidence["matches"].append({
                "product_id": r["product_id"], "name": r["name"], "heisse_id": aid,
                "image_url": url, "bytes": clen, "content_type": ctype,
                "heisse_price": xs[0].get("price"),
                "heisse_price_date": ((xs[0].get("priceHistory") or [{}])[0] or {}).get("date"),
            })
        else:
            evidence["failed_head"].append({
                "product_id": r["product_id"], "name": r["name"], "heisse_id": aid,
                "url": url, "status": st, "content_type": ctype, "bytes": clen,
            })
        if checked % 25 == 0:
            print(f"  checked {checked}: ok={len(evidence['matches'])} fail={len(evidence['failed_head'])}")

    evidence["summary"] = {
        "checked": checked,
        "matched_ok": len(evidence["matches"]),
        "failed_head": len(evidence["failed_head"]),
        "unmatched": len(evidence["unmatched"]),
    }
    print("summary", evidence["summary"])

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(RAW, exist_ok=True)
    raw_path = os.path.join(RAW, f"spar_cdn_images_{day}.json")
    if not args.dry_run:
        json.dump(evidence, open(raw_path, "w"), ensure_ascii=False, indent=2)
        print("wrote", raw_path)

        for r in products:
            if r["product_id"] in updates_by_pid:
                r["image_url"] = updates_by_pid[r["product_id"]]
                # keep provenance in source if empty-ish; append note via not inventing new columns
                if r.get("source") and "spar-cdn" not in r["source"]:
                    pass  # source stays the original product source; image provenance is in raw/
        write_products(products)
        print("updated data/products.*", len(updates_by_pid), "images")

        if args.patch_app:
            n = patch_app(args.patch_app, updates_by_pid, updates_by_norm)
            print("patched app data.json", n)

        if args.patch_sources:
            for p in (
                "/workspace/fertig/expand.json",
                "/workspace/fertig/brandfam_products.json",
                "/workspace/fertig/classics_ext.json",
            ):
                n = patch_list_json(p, updates_by_norm)
                print("patched", p, n)
    else:
        print("dry-run, not writing")


if __name__ == "__main__":
    main()
