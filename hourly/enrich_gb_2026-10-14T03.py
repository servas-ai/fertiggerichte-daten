# hourly T03: enrich hand-picked Gurkerl/BILLA hits (composition/detail APIs) -> nutrition/EAN/producer
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters.rewe import Billa
from food_connectors.schema import Product
P={p['source_id']:p for f in ('/tmp/h03/s1.json','/tmp/h03/s2.json','/tmp/h03/s3.json') for p in json.load(open(f))}
SEL={'25925':'g','9600':'g','45894':'g','45859':'g'}
g=Gurkerl(); b=Billa(); out=[]
for sid,src in SEL.items():
    d=dict(P[sid]); d.pop('_src',None); p=Product(**{k:v for k,v in d.items() if k in Product.__dataclass_fields__})
    if src=='g':
        st=g.products([sid])[0]; p.extra=dict(p.extra or {},in_stock=st.extra.get('in_stock'))
    try: (g if src=='g' else b).enrich(p)
    except Exception as e: print('ERR',sid,e)
    time.sleep(0.4); out.append(dict(p.__dict__,_src=src)); e=p.extra or {}
    print(sid,'|',p.name,'|',p.price_eur,p.size_g,'|',p.nutrition_100g,'|',p.ean,'|',(p.producer or '')[:60].replace('\n',' '),'|',p.producer_id,'|',e.get('in_stock'),e.get('storage'),flush=True)
json.dump(out,open('hourly/cand_gb2_2026-10-14T03.json','w'),ensure_ascii=False,default=str,indent=0)
