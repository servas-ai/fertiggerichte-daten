"""T1938 probe: de/en Wikipedia infobox (lead section wikitext) of the identifier-matched Wikidata items from wikidata_out.json.
Infobox Unternehmen / Infobox company fields: Gründungsdatum/founded, Mitarbeiterzahl/num_employees, Umsatz/revenue, Stand/*_year.
1 req/s. Output wikipedia_out.json."""
import json, re, time, urllib.parse, urllib.request
UA = "food-connectors/0.1 (+https://github.com/servas-ai/fertiggerichte-daten)"
def get(u):
    time.sleep(1.1); return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=40))
W = json.load(open("scripts/facts_T1938/wikidata_out.json"))
items = sorted({x["item"].rsplit("/", 1)[1] for v in W.values() for x in v})
links = {}
for i in range(0, len(items), 40):
    d = get("https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks&sitefilter=dewiki|enwiki|itwiki&format=json&ids=" + "|".join(items[i:i + 40]))
    for q, e in d["entities"].items(): links[q] = {k: v["title"] for k, v in (e.get("sitelinks") or {}).items()}
FIELDS = re.compile(r"^\s*\|\s*(Gründungsdatum|Gründung|Mitarbeiterzahl|Mitarbeiter|Umsatz|Stand|Sitz|Rechtsform|founded|foundation|num_employees|num_employees_year|revenue|revenue_year|location|hq_location_city|fondazione|dipendenti|fatturato)\s*=\s*(.*)$", re.M)
out = {}
for q, l in links.items():
    for wiki, title in l.items():
        lang = wiki[:2]
        try:
            d = get(f"https://{lang}.wikipedia.org/w/api.php?action=parse&prop=wikitext&section=0&format=json&page=" + urllib.parse.quote(title))
            wt = d["parse"]["wikitext"]["*"]
            out.setdefault(q, {})[wiki] = {"title": title, "url": f"https://{lang}.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(' ', '_')),
                                           "fields": {k: v.strip() for k, v in FIELDS.findall(wt)}}
        except Exception as e: out.setdefault(q, {})[wiki] = {"title": title, "error": str(e)[:100]}
json.dump(out, open("scripts/facts_T1938/wikipedia_out.json", "w"), ensure_ascii=False, indent=1)
for q, v in out.items():
    for w, x in v.items(): print(q, w, x.get("title"), json.dumps(x.get("fields"), ensure_ascii=False)[:600])
