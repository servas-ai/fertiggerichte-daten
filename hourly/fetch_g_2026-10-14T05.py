# hourly T05: enrich hand-picked Gurkerl candidates (new sitemap categories) via public composition/details API
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
IDS=[int(x) for x in sys.argv[1].split(',')]
g=Gurkerl(); out=[]
for p in g.products(IDS):
    g.enrich(p); time.sleep(0.3)
    out.append(p.__dict__)
    print(p.source_id,'|',p.name,'|',p.price_eur,p.size_g,'|',p.ean,'|',p.nutrition_100g,'|',(p.producer or '')[:50],'|',p.producer_id,'|',p.extra.get('in_stock'))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,default=str,indent=0)
