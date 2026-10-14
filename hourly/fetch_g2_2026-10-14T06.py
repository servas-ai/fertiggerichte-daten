# hourly T06: fetch fresh card/price/stock + composition for hand-picked Gurkerl ids from the T05 sitemap-category walk leftovers
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.http import get
IDS=[6076,37024,22186,45896,49654,34801,14035,25552,46435,6615,6618,6617,6616,6614,43196,43195,29857]
g=Gurkerl(); out=[]
ps=g.products(IDS,'T06 sitemap-category leftovers')
for p in ps:
  g.enrich(p); time.sleep(0.3)
  try:
    d=get(f'https://www.gurkerl.at/api/v1/products/{p.source_id}/details')['product']
    p.extra['storage']=[x.get('name') if isinstance(x,dict) else x for x in (d.get('storage') or d.get('storageConditions') or [])] if isinstance(d,dict) else None
    p.extra['detail_keys']=list(d.keys())[:40]
    p.extra['cats']=[c.get('name') for c in d.get('categories') or [] if isinstance(c,dict)]
  except Exception as e: p.extra['detail_err']=str(e)
  out.append(p.__dict__)
  n=p.nutrition_100g or {}
  print(p.source_id,'|',p.name[:55],'|',p.price_eur,p.size_g,'| stock',p.extra.get('in_stock'),'| kcal',n.get('kcal'),'P',n.get('protein'),'F',n.get('fat'),'C',n.get('carbs'),'|',(p.producer or '')[:40],'|',p.producer_id,'|',p.ean,'| img',bool(p.image_url),flush=True)
json.dump(out,open('/tmp/h06/g_cand2.json','w'),ensure_ascii=False,default=str)
