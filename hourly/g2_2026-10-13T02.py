import sys,json,re,dataclasses,concurrent.futures as cf
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
idx=json.load(open('idx_2026-10-13T02.json'));N=set(idx['names']);E=set(idx['eans']);U=set(idx['urls'])
norm=lambda s: re.sub(r'[^a-z0-9äöüß]','',(s or '').lower())
g=Gurkerl();ps=g.fetch()
print('category products',len(ps))
ps=[p for p in ps if p.extra.get('in_stock') and norm(p.name) not in N and p.source_url not in U and not any(p.source_id in u for u in U if 'gurkerl' in u)]
print('new in stock',len(ps))
with cf.ThreadPoolExecutor(8) as ex: ps=list(ex.map(g.enrich,ps))
ps=[p for p in ps if not (p.ean and p.ean in E)]
json.dump([dataclasses.asdict(p) for p in ps],open('cand_gurkerl_cat_2026-10-13T02.json','w'),ensure_ascii=False,indent=1)
for p in ps: print(p.source_id,'|',p.name,'|',p.category.split(' > ')[-1],'|',p.price_eur,p.size_g,'|',bool(p.nutrition_100g),p.ean,p.producer_id)
