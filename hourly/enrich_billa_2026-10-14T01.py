# hourly T01: enrich hand-picked BILLA heat-up candidates via detail API
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for p in json.load(open('/tmp/h01/billa_new.json'))}
SEL="00-10042 00-708562 00-886427 00-901948 00-723753 00-723755 00-404589 00-416106 00-909535 00-431606 00-868704 00-746319 00-667910 00-730112 00-82502 00-3298 00-605251 00-886410".split()
b=Billa(); out=[]
for sid in SEL:
    if sid not in P: print('MISS',sid); continue
    d=P[sid]; p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    try: b.enrich(p)
    except Exception as e: print('ERR',sid,e)
    time.sleep(0.35)
    out.append(p.__dict__); e=p.extra or {}; n=p.nutrition_100g or {}
    print(sid,'|',p.name,'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',p.ean,'|',(p.producer or '')[:40].replace('\n',' '),'|',e.get('storage'),e.get('in_promotion'),e.get('price_standard_eur'),flush=True)
json.dump(out,open('hourly/cand_billa_2026-10-14T01.json','w'),ensure_ascii=False,default=str,indent=0)
print('enriched',len(out))
