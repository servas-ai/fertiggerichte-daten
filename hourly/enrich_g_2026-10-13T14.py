import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
g=Gurkerl()
P={p['source_id']:p for p in json.load(open('/tmp/h14/g_new.json'))}
SEL=[25925,25923,3602,48227,9600,6085,6087,36982,2670,6082,6084,40110,13201,13214,30668,2669,36984,6095,2673,39459,6098,6101,36972,13210,13220,13190,22185,22186,39477,42082,42081,45896,39476,47753,30832,36976,36978,36979,22935,33501,5931,5932,28302,31909,5944,28303,27400,31876,44155,31874,38457,30833]
ids=[i for i in SEL if str(i) in P]
ps=g.products(ids,None)
out=[]
for p in ps:
    p.category=P[p.source_id]['category'] if p.source_id in P else p.category
    if p.extra.get('archived') or not p.extra.get('in_stock'): print('SKIP stock',p.name,p.extra.get('in_stock')); continue
    g.enrich(p); time.sleep(0.3)
    out.append(p.__dict__)
    print(p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:50],'|',p.producer_id,'|',p.origin)
json.dump(out,open('hourly/cand_gurkerl_2026-10-13T14.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
