# hourly T18: enrich hand-picked Gurkerl ready-meal candidates (composition API -> nutrition/EAN/producer/Identitätskennzeichen)
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.schema import Product
g=Gurkerl()
P={p['source_id']:p for p in json.load(open('/tmp/h18/g_new.json'))}
SEL=[40024,25925,33405,37023,21866]
out=[]
for i in SEL:
    d=P.get(str(i))
    if not d: print('MISSING',i); continue
    p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    g.enrich(p); time.sleep(0.3); out.append(p.__dict__)
    print(p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:50].replace('\n',' '),'|',p.producer_id,'|',p.origin,flush=True)
json.dump(out,open('hourly/cand_gurkerl_2026-10-13T18.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
