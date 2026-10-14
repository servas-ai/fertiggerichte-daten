"""Strict logo-less brand/product count, same logic as fertiggerichte-hub/scripts/coverage.py (file-backed rows only)."""
import csv, collections, json, sys
D = "/workspace/fertiggerichte-daten/data"
P = list(csv.DictReader(open(f"{D}/products.csv"))); L = list(csv.DictReader(open(f"{D}/logos.csv")))
LF = [l for l in L if (l.get("file") or "").strip()]
nm = lambda R: {l["name"].lower() for l in R} | {l["slug"] for l in R} | {b.lower() for l in R for b in (l.get("brands") or "").split("|") if b}
lf, la = nm(LF), nm(L)
bc = collections.Counter(p["brand"].strip() for p in P if p.get("brand", "").strip())
bm = [(b, n) for b, n in bc.most_common() if b.lower() not in lf]
br = [(b, n) for b, n in bc.most_common() if b.lower() not in la]
out = dict(products=len(P), brands=len(bc), strict_brands=len(bm), strict_products=sum(n for _, n in bm),
           lenient_brands=len(br), lenient_products=sum(n for _, n in br), rows=len(L), with_file=len(LF), top=bm[:12])
print(json.dumps(out, ensure_ascii=False))
