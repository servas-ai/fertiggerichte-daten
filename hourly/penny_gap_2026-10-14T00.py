# hourly T00 (2026-10-14T00): PENNY online assortment (penny-shop listing) — ready-meal items not yet in scored/connectors_new (url, sku or name+store)
import sys,json,re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import penny_shop as P
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}; names={k(x['name']) for x in S if 'penny' in str(x.get('store')).lower()}
L=[P.to_product(r) for r in P.listing()]
out=[]
for p in L:
  if p.source_url in urls or k(p.name) in names: continue
  if P.is_ready_meal(p):
    out.append(p.__dict__); print(p.source_id,'|',p.name,'|',p.price_eur,p.size_g,'|',p.category)
json.dump(out,open('/tmp/h00/penny_new.json','w'),ensure_ascii=False,default=str)
print(len(L),len(out))
