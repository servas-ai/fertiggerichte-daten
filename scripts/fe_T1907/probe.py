import json, time, urllib.request, urllib.parse
d=json.load(open('../../data/companies.json'))
UA={'User-Agent':'servas-fertiggerichte-daten/1.0 (https://github.com/servas-ai/fertiggerichte-daten; data squad)','Accept':'application/json'}
def get(u):
    req=urllib.request.Request(u,headers=UA); return json.load(urllib.request.urlopen(req,timeout=60))
out={'gleif':{},'wikidata':{}}
leis={r['lei']:r['slug'] for r in d if r.get('lei')}
L=list(leis)
for i in range(0,len(L),50):
    j=get('https://api.gleif.org/api/v1/lei-records?page[size]=50&filter[lei]='+','.join(L[i:i+50]))
    for rec in j['data']:
        e=rec['attributes']['entity']
        out['gleif'][leis[rec['id']]]={'lei':rec['id'],'creationDate':e.get('creationDate'),'legalName':e['legalName']['name'],'status':e.get('status')}
    time.sleep(1)
vat={r['uid'].replace(' ',''):r['slug'] for r in d if r.get('uid')}
def sparql(values_var,prop,vals):
    q=f"""SELECT ?v ?item ?itemLabel ?inception ?emp ?empTime ?rev ?revTime ?revUnitLabel ?site WHERE {{
 VALUES ?v {{ {' '.join(json.dumps(x) for x in vals)} }}
 ?item wdt:{prop} ?v .
 OPTIONAL {{ ?item wdt:P571 ?inception }}
 OPTIONAL {{ ?item p:P1128 ?es . ?es ps:P1128 ?emp . OPTIONAL {{ ?es pq:P585 ?empTime }} }}
 OPTIONAL {{ ?item p:P2139 ?rs . ?rs psv:P2139 ?rv . ?rv wikibase:quantityAmount ?rev ; wikibase:quantityUnit ?revUnit . OPTIONAL {{ ?rs pq:P585 ?revTime }} }}
 OPTIONAL {{ ?item wdt:P856 ?site }}
 SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,en". }} }}"""
    return get('https://query.wikidata.org/sparql?format=json&query='+urllib.parse.quote(q))['results']['bindings']
for prop,m in (('P1278',leis),('P3608',vat)):
    vals=list(m)
    for i in range(0,len(vals),40):
        for b in sparql('v',prop,vals[i:i+40]):
            s=m[b['v']['value']]
            x={k:v['value'] for k,v in b.items()}; x['matched_by']=prop
            out['wikidata'].setdefault(s,[]).append(x)
        time.sleep(2)
json.dump(out,open('probe_out.json','w'),ensure_ascii=False,indent=1)
print('gleif',len(out['gleif']),'with creationDate',sum(1 for v in out['gleif'].values() if v['creationDate']))
print('wikidata slugs',len(out['wikidata']))
for s,v in out['wikidata'].items():
    print(s, v[0]['item'], v[0].get('itemLabel'), {x.get('inception') for x in v}, {(x.get('emp'),x.get('empTime')) for x in v}, {(x.get('rev'),x.get('revUnitLabel'),x.get('revTime')) for x in v})
