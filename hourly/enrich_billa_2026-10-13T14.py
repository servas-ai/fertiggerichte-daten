import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for p in json.load(open('/tmp/h14/billa_new.json'))}
SEL="00-3046 00-704957 00-737146 00-667911 00-727877 00-822524 00-443214 00-435103 00-943210 00-616589 00-739059 00-749364 00-761806 00-643610 00-789342 00-468948 00-719357 00-521760 00-737917 00-757650 00-757649 00-440314 00-680780 00-680782 00-680785 00-718798 00-799966 00-869290".split()
b=Billa(); out=[]
for sid in SEL:
    d=P[sid]; p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    b.enrich(p); time.sleep(0.4)
    out.append(p.__dict__); print(p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:50].replace('\n',' '),'|',p.producer_id,'|',(p.extra or {}).get('ingredients','')[:0])
json.dump(out,open('hourly/cand_billa_2026-10-13T14.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
