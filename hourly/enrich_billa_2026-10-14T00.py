# hourly T00 (2026-10-14T00): enrich hand-picked BILLA hits (T00 brand/dish stem search) via product-discovery detail API -> nutrition/EAN/producer/storage/regular price
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for p in json.load(open('/tmp/h00/billa_new.json'))}
SEL="00-692685 00-746412 00-616605 00-721002 00-723595 00-878830 00-889324 00-648634 00-447286 00-892041 00-892049".split()
b=Billa(); out=[]
for sid in SEL:
    d=P[sid]; p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    try: b.enrich(p)
    except Exception as e: print('ERR',sid,e)
    time.sleep(0.4)
    out.append(p.__dict__); e=p.extra or {}
    print(sid,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:45].replace('\n',' '),'|',p.producer_id,'|',e.get('storage'),str(e.get('category_path',''))[:50],e.get('in_promotion'),e.get('price_standard_eur'),flush=True)
json.dump(out,open('hourly/cand_billa_2026-10-14T00.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
