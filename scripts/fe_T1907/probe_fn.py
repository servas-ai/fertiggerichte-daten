import json, time, urllib.request, urllib.parse, re
d=json.load(open('../../data/companies.json'))
UA={'User-Agent':'servas-fertiggerichte-daten/1.0 (https://github.com/servas-ai/fertiggerichte-daten; data squad)','Accept':'application/json'}
def get(u): return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90))
m={}
for r in d:
    fn=(r.get('fn') or '').replace('FN','').strip().replace(' ','')
    if re.fullmatch(r'\d+[a-z]',fn): m[fn]=r['slug']
print(len(m))
vals=' '.join(json.dumps(x) for x in m)
q=f"""SELECT ?v ?item ?itemLabel ?inception ?emp ?empTime ?rev ?revTime ?revUnitLabel ?site WHERE {{
 VALUES ?v {{ {vals} }} ?item wdt:P5285 ?v .
 OPTIONAL {{ ?item wdt:P571 ?inception }}
 OPTIONAL {{ ?item p:P1128 ?es . ?es ps:P1128 ?emp . OPTIONAL {{ ?es pq:P585 ?empTime }} }}
 OPTIONAL {{ ?item p:P2139 ?rs . ?rs psv:P2139 ?rv . ?rv wikibase:quantityAmount ?rev ; wikibase:quantityUnit ?revUnit . OPTIONAL {{ ?rs pq:P585 ?revTime }} }}
 OPTIONAL {{ ?item wdt:P856 ?site }}
 SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,en". }} }}"""
b=get('https://query.wikidata.org/sparql?format=json&query='+urllib.parse.quote(q))['results']['bindings']
out={}
for x in b:
    y={k:v['value'] for k,v in x.items()}; y['matched_by']='P5285'; out.setdefault(m[y['v']],[]).append(y)
# sample format
s=get('https://query.wikidata.org/sparql?format=json&query='+urllib.parse.quote('SELECT ?v WHERE { ?i wdt:P5285 ?v } LIMIT 5'))
print([x['v']['value'] for x in s['results']['bindings']])
json.dump(out,open('probe_fn_out.json','w'),ensure_ascii=False,indent=1)
for s,v in out.items():
    print(s, v[0]['item'], v[0].get('itemLabel'), sorted({x.get('inception') for x in v if x.get('inception')}), sorted({(x.get('emp'),x.get('empTime')) for x in v if x.get('emp')}), sorted({(x.get('rev'),x.get('revUnitLabel'),x.get('revTime')) for x in v if x.get('rev')}))
