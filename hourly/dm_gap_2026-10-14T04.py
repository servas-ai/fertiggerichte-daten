# hourly T04: dm sitemap ready-meal slugs not yet in dataset -> fetch product JSON (nutrition/GTIN/price)
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import dm_shop as D
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
have={m.group(1) for x in S for m in [re.search(r'/p/d/(\d+)',str(x.get('url') or ''))] if m}
haveE={str(x.get('ean')).lstrip('0') for x in S if x.get('ean') and str(x.get('store')).lower()=='dm'}
U=[u for u in D.sitemap_urls() if D.SLUG.search(u.rsplit('/',1)[1]) and not D.SLUG_NOT.search(u.rsplit('/',1)[1])]
gap=[u for u in U if re.search(r'/p/d/(\d+)',u).group(1) not in have]
print('slugs',len(U),'gap',len(gap),flush=True)
out=[]
for u in gap[:80]:
  dan=int(re.search(r'/p/d/(\d+)/',u).group(1))
  try: p=D.product(dan,u)
  except Exception as e: print('ERR',u,e); continue
  time.sleep(0.8)
  if p.ean and str(p.ean).lstrip('0') in haveE: continue
  out.append(p.__dict__); n=p.nutrition_100g or {}
  print(dan,'|',D.is_ready_meal(p),'|',(p.extra or {}).get('breadcrumbs'),'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',p.ean,flush=True)
json.dump(out,open('/tmp/h04/dm_gap.json','w'),ensure_ascii=False,default=str)
