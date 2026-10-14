# hourly T04: full BILLA public catalog listing (product-discovery/products, 100/page) -> meal-category items not yet in dataset
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa, get
b=Billa(); out=[]
for page in range(130):
    try: d=get(f'https://shop.billa.at/api/product-discovery/products?page={page}&pageSize=100')
    except Exception as e: print('ERR',page,e,flush=True); time.sleep(3); continue
    rs=d.get('results',[]); out+=rs
    print(page,len(rs),len(out),flush=True)
    if len(rs)<100: break
    time.sleep(0.6)
json.dump(out,open('/tmp/h04/billa_all.json','w'),ensure_ascii=False,default=str)
print('TOTAL',len(out))
