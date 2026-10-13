# hourly T22: enrich hand-picked BILLA leftovers (T20 search walk) via product-discovery detail API -> nutrition/EAN/producer/storage/regular price
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for p in json.load(open('/tmp/h20/billa_new.json'))}
SEL="00-423347 00-822507 00-730948 00-306542 00-306554 00-13992 00-886424 00-680707 00-891310 00-758304 00-891835 00-692685 00-892041 00-892049 00-730177 00-578894 00-894631 00-605251".split()
b=Billa(); out=[]
for sid in SEL:
    d=P[sid]; p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    b.enrich(p); time.sleep(0.4)
    out.append(p.__dict__); e=p.extra or {}
    print(sid,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:45].replace('\n',' '),'|',p.producer_id,'|',e.get('storage'),e.get('category_path','')[:40],e.get('in_promotion'),e.get('price_standard_eur'),flush=True)
json.dump(out,open('hourly/cand_billa_2026-10-13T22.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
