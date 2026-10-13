# hourly T16: enrich hand-picked BILLA candidates (product detail API -> nutrition/EAN/producer/storage)
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for p in json.load(open('/tmp/h16/billa_new.json'))}
SEL="00-578449 00-578451 00-427523 00-774595 00-855042 00-693128 00-693125 00-693126 00-19291 00-4932 00-417097 00-501322 00-8224 00-433286 00-894426 00-733528 00-741177 00-419222 00-538048 00-864846 00-892041 00-892049".split()
b=Billa(); out=[]
for sid in SEL:
    d=P[sid]; p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    b.enrich(p); time.sleep(0.4)
    out.append(p.__dict__); e=p.extra or {}
    print(p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:45].replace('\n',' '),'|',p.producer_id,'|',e.get('storage'),e.get('category_path','')[:40],e.get('in_promotion'),e.get('price_standard_eur'),flush=True)
json.dump(out,open('hourly/cand_billa_2026-10-13T16.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
