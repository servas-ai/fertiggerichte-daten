# hourly T17: enrich hand-picked BILLA candidates (product detail API -> nutrition/EAN/producer/storage)
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for p in json.load(open('/tmp/h17/billa_new.json'))}
SEL="00-692684 00-692685 00-903264 00-903261 00-890864 00-890861 00-871240 00-871241 00-871244 00-905180 00-645050 00-903231 00-774589 00-855724 00-348973 00-763125 00-737146".split()
b=Billa(); out=[]
for sid in SEL:
    d=P[sid]; p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    b.enrich(p); time.sleep(0.4)
    out.append(p.__dict__); e=p.extra or {}
    print(p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:45].replace('\n',' '),'|',p.producer_id,'|',e.get('storage'),e.get('category_path','')[:40],e.get('in_promotion'),e.get('price_standard_eur'),flush=True)
json.dump(out,open('hourly/cand_billa_2026-10-13T17.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
