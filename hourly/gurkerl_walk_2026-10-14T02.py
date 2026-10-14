# hourly T02: Gurkerl ready-meal category walk — in-stock ids not yet in scored/connectors_new nor inspected
import json,sys,re,glob
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl, MEAL_CATEGORIES
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
hn={k(x['name']) for x in S if 'gurkerl' in str(x.get('store')).lower()}
insp=set()
for f in glob.glob('/workspace/fertig/hourly/cand_gurkerl*.json'):
  try: insp|={str(p.get('source_id')) for p in json.load(open(f))}
  except Exception: pass
g=Gurkerl(); out=[]
print(MEAL_CATEGORIES)
for p in g.fetch():
  if p.source_id in have or p.source_id in insp or k(p.name) in hn: continue
  if not p.extra.get('in_stock'): continue
  out.append(p.__dict__)
json.dump(out,open('/tmp/h02/g_walk.json','w'),ensure_ascii=False,default=str)
print('new in-stock',len(out))
for p in out: print(p['source_id'],'|',p['category'],'|',p['brand'],'|',p['name'],'|',p['price_eur'],p['size_g'])
