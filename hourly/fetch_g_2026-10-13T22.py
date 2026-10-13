# hourly T22: fresh Gurkerl ready-meal category walk (food-connectors gurkerl MEAL_CATEGORIES) -> only ids not yet in scored/connectors_new, in stock
import json,sys,re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
g=Gurkerl(); ps=g.fetch('ready-meals',5000)
new=[p for p in ps if p.source_id not in have and p.extra.get('in_stock')]
print('walk',len(ps),'new in stock',len(new))
for p in new: g.enrich(p)
json.dump([p.__dict__ for p in new],open('hourly/cand_gurkerl_walk_2026-10-13T22.json','w'),ensure_ascii=False,default=str,indent=0)
for p in new: print(p.source_id,'|',p.category,'|',p.name,'|',p.price_eur,p.size_g,'|',(p.nutrition_100g or {}).get('kcal'),(p.nutrition_100g or {}).get('protein'),'|',p.ean)
