# hourly T23: enrich hand-picked BILLA hits (T23 brand-stem search) via product-discovery detail API -> nutrition/EAN/producer/storage/regular price
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for p in json.load(open('/tmp/h23/billa_new.json'))}
SEL="00-774139 00-382821 00-736994 00-648626 00-723599 00-734526 00-723600 00-774425 00-774429".split()
b=Billa(); out=[]
for sid in SEL:
    d=P[sid]; p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    try: b.enrich(p)
    except Exception as e: print('ERR',sid,e)
    time.sleep(0.4)
    out.append(p.__dict__); e=p.extra or {}
    print(sid,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:45].replace('\n',' '),'|',p.producer_id,'|',e.get('storage'),str(e.get('category_path',''))[:40],e.get('in_promotion'),e.get('price_standard_eur'),flush=True)
json.dump(out,open('hourly/cand_billa_2026-10-13T23.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
