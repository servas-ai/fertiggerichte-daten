# hourly T22: enrich hand-picked leftover Gurkerl candidates (T20 walk) via composition API -> nutrition/EAN/producer/Identitätskennzeichen; fresh price/stock via products API
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.schema import Product
g=Gurkerl()
P={p['source_id']:p for f in ('/tmp/h20/g_new.json','/tmp/h20/g2_new.json','/tmp/h20/g3_new.json') for p in json.load(open(f))}
SEL=[45894,22185,22186,21878,5909,5952,29967,31528,31529,31530,42103,6795,2673,46402,4144,44765,6084,25925,21866,4119]
out=[]
for i in SEL:
    d=P.get(str(i))
    if not d: print('MISSING',i); continue
    try:
        fr=g.products([i],category=d.get('category'))
        if fr: d={**d,**{k:v for k,v in fr[0].__dict__.items() if v not in (None,{},'')}}
    except Exception as e: print('PRICE-ERR',i,e)
    p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    try: g.enrich(p)
    except Exception as e: print('ENRICH-ERR',i,e)
    time.sleep(0.3); out.append(p.__dict__)
    print(i,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:50].replace('\n',' '),'|',p.producer_id,'|',(p.extra or {}).get('in_stock'),flush=True)
json.dump(out,open('hourly/cand_gurkerl_2026-10-13T22.json','w'),ensure_ascii=False,default=str,indent=0)
print(len(out))
