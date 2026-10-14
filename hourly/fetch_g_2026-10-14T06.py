# hourly T06: fetch fresh card/price/stock + composition for hand-picked Gurkerl ids from the T05 sitemap-category walk leftovers
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.http import get
IDS=[29852,13112,13107,21157,21149,36121,43980,40005,46402,25856,49066,28394,
 35820,1590,1592,1591,1596,1597,32681,32675,32669,32674,32682,32679,47579,39172,39171,39173,25565,46107,10705,47993,47994,47992,47991,
 5950,41319,41318,5490,28393,11755,12968,26411,26412,10853,42675,42080,42083,40837,40842]
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
json.dump(out,open('/tmp/h06/g_cand.json','w'),ensure_ascii=False,default=str)
