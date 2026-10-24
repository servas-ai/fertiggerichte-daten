import json,sys,re,dataclasses
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl, MEAL_CATEGORIES
g=Gurkerl()
d=json.load(open('/workspace/fertig-app/public/data.json'))['rows']
eans={str(r.get('ean')) for r in d if r.get('ean')}
names={(r.get('name') or '').lower().strip() for r in d}
urlids=set()
for r in d:
    m=re.search(r'gurkerl\.at/(\d+)-',r.get('url') or '')
    if m: urlids.add(m.group(1))
for f in ['staged_2026-10-24T17.json','staged_2026-10-24T18.json']:
    for r in json.load(open(f)):
        eans.add(str(r.get('ean'))); names.add(r['name'].lower().strip()); urlids.add(str(r.get('source_id')))
cats=[906,620,137872,137873,312,380,379,135049,135050,135051,134260,602,136143]
seen=set(); out=[]
for cid in cats:
    try: ids=[i for i in g.category_ids(cid,limit=1000) if i not in seen and str(i) not in urlids]
    except Exception as e: print('err',cid,e); continue
    seen.update(ids)
    ps=[p for p in g.products(ids, MEAL_CATEGORIES[cid]) if not p.extra.get('archived')]
    ps=[p for p in ps if p.name.lower().strip() not in names]
    print(cid, MEAL_CATEGORIES[cid], len(ids), 'new cand', len(ps))
    out+=ps
json.dump([dataclasses.asdict(p) for p in out],open('/tmp/gk_cand.json','w'),ensure_ascii=False,indent=0)
print(len(out))
