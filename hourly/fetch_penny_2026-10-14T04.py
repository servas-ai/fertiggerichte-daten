# hourly T04: Penny online-assortment ready meals not yet present; nutrition via identical BILLA article 00-<REWE no.>
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import penny_shop as P
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
rs=P.listing()
ps=[P.to_product(r) for r in rs]
print('listing',len(ps))
out=[p.__dict__ for p in ps if p.source_url not in urls]
json.dump(out,open('/tmp/h04/penny_all_new.json','w'),ensure_ascii=False,default=str)
for p in out: print(p['source_id'],'|',p['category'],'|',p['brand'],'|',p['name'],'|',p['price_eur'],p['size_g'],'| meal' if P.is_ready_meal(P.Product(**p)) else '')
