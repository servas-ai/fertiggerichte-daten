# hourly T00 (2026-10-14T00): fresh stock/price + composition for hand-picked Gurkerl ids from search_g_2026-10-14T00.py
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
C={p['source_id']:p for p in json.load(open('/tmp/h00/g_cands.json'))}
SEL=['5910','32859','36971','45599','45598','45600']
g=Gurkerl(); out=[]
for p in g.products([int(x) for x in SEL]):
    p.category=C.get(p.source_id,{}).get('category')
    if not p.extra.get('in_stock') or p.extra.get('archived'): print('NOSTOCK',p.source_id,p.name); continue
    try: g.enrich(p)
    except Exception as e: print('ENRICH-ERR',p.source_id,e)
    time.sleep(0.3); out.append(p.__dict__)
    print(p.source_id,'|',p.category,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:40].replace('\n',' '),'|',p.producer_id,flush=True)
json.dump(out,open('hourly/cand_gurkerl_search_2026-10-14T00.json','w'),ensure_ascii=False,default=str,indent=0)
print('instock',len(out))
