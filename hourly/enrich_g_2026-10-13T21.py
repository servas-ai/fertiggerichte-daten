# hourly T21: enrich hand-picked (leftover T20 walk) Gurkerl ready-meal candidates (composition API -> nutrition/EAN/producer/Identitätskennzeichen)
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.schema import Product
g=Gurkerl()
P={p['source_id']:p for f in ('/tmp/h20/g_new.json','/tmp/h20/g2_new.json','/tmp/h20/g3_new.json') for p in json.load(open(f))}
SEL=[49189,49190,49191,49192,25925,2673,6084,33500,45894,31596,46873,46871,3458,3453]
out=[]
for i in SEL:
    d=P.get(str(i))
    if not d: print('MISSING',i); continue
    p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    g.enrich(p); time.sleep(0.3); out.append(p.__dict__)
    print(p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:50].replace('\n',' '),'|',p.producer_id,'|',p.origin,flush=True)
json.dump(out,open('hourly/cand_gurkerl_2026-10-13T21.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
