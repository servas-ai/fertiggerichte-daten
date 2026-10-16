"""T1938 probe: Wikidata items matched by identifier only — LEI (P1278) or official website (P856) whose IRI equals a
variant (http/https, www/no-www, trailing slash) of the row's verified website domain root. Returns P1128 employees,
P2139 revenue (with P585 point in time + unit), P571 inception, P17 country, P31 instance-of labels. Output wikidata_out.json."""
import csv, json, time, urllib.parse, urllib.request
UA = "food-connectors/0.1 (+https://github.com/servas-ai/fertiggerichte-daten)"
def sparql(q):
    time.sleep(1.2)
    req = urllib.request.Request("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q), headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=90))["results"]["bindings"]
SEL = """SELECT ?key ?item ?itemLabel ?site ?inception ?emp ?empTime ?rev ?revTime ?revUnitLabel ?countryLabel ?typeLabel WHERE {{
 VALUES ?key {{ {vals} }} {pat}
 OPTIONAL {{ ?item wdt:P856 ?site }} OPTIONAL {{ ?item wdt:P571 ?inception }}
 OPTIONAL {{ ?item p:P1128 ?es. ?es ps:P1128 ?emp. OPTIONAL {{ ?es pq:P585 ?empTime }} }}
 OPTIONAL {{ ?item p:P2139 ?rs. ?rs psv:P2139 ?rv. ?rv wikibase:quantityAmount ?rev; wikibase:quantityUnit ?revUnit. OPTIONAL {{ ?rs pq:P585 ?revTime }} }}
 OPTIONAL {{ ?item wdt:P17 ?country }} OPTIONAL {{ ?item wdt:P31 ?type }}
 SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,en,it,fr,nl". }} }}"""
rows = list(csv.DictReader(open("data/companies.csv")))
out = {}
lei = {}
for r in rows:
    if r["lei"]: lei.setdefault(r["lei"], []).append(r["slug"])
L = list(lei)
for i in range(0, len(L), 40):
    vals = " ".join(f'"{x}"' for x in L[i:i + 40])
    for b in sparql(SEL.format(vals=vals, pat="?item wdt:P1278 ?key .")):
        x = {k: v["value"] for k, v in b.items()}; x["matched_by"] = "P1278 LEI"
        for s in lei[x["key"]]: out.setdefault(s, []).append(x)
site = {}
for r in rows:
    w = r["website"].strip()
    if not w: continue
    host = urllib.parse.urlparse(w).netloc.lower().replace("www.", "")
    for sch in ("http", "https"):
        for pre in ("", "www."):
            for tail in ("", "/", "/de/", "/at/", "/de", "/de-at/"):
                site.setdefault(f"{sch}://{pre}{host}{tail}", set()).add(r["slug"])
S = list(site)
for i in range(0, len(S), 120):
    vals = " ".join(f"<{x}>" for x in S[i:i + 120])
    for b in sparql(SEL.format(vals=vals, pat="?item wdt:P856 ?key .")):
        x = {k: v["value"] for k, v in b.items()}; x["matched_by"] = "P856 official website = row website"
        for s in site[x["key"]]: out.setdefault(s, []).append(x)
json.dump(out, open("scripts/facts_T1938/wikidata_out.json", "w"), ensure_ascii=False, indent=1)
for s, v in out.items():
    items = sorted({(x["item"].rsplit("/", 1)[1], x.get("itemLabel"), x["matched_by"][:5]) for x in v})
    emp = sorted({(x.get("emp"), (x.get("empTime") or "")[:4]) for x in v if x.get("emp")})
    rev = sorted({(x.get("rev"), (x.get("revTime") or "")[:4], x.get("revUnitLabel")) for x in v if x.get("rev")})
    inc = sorted({x["inception"][:10] for x in v if x.get("inception")})
    print(s, items, "EMP", emp, "REV", rev, "INC", inc, sorted({x.get("typeLabel") for x in v}))
