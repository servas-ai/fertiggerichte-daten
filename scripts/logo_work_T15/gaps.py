import csv, collections, sys
D="/workspace/fertiggerichte-daten/data"
P=list(csv.DictReader(open(f"{D}/products.csv"))); L=list(csv.DictReader(open(f"{D}/logos.csv")))
LF=[l for l in L if (l.get("file") or "").strip()]
names=lambda LL:{l["name"].lower() for l in LL}|{l["slug"] for l in LL}|{b.lower() for l in LL for b in (l.get("brands") or "").split("|") if b}
lf=names(LF); la=names(L)
bc=collections.Counter(p["brand"].strip() for p in P if p.get("brand","").strip())
ch=collections.defaultdict(set)
for p in P: ch[p["brand"].strip()].add(p["chain"])
miss=[(b,n) for b,n in bc.most_common() if b.lower() not in lf]
print(len(miss), sum(n for _,n in miss), "LF", len(LF), len(L))
if len(sys.argv)>1:
  for b,n in miss: print(n, b, sorted(ch[b]), "ROW" if b.lower() in la else "")
