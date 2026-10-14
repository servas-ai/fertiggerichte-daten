# hourly T05: Gurkerl categories from public sitemap_base.xml not in adapter MEAL_CATEGORIES — list in-stock ids not yet in dataset
import json,sys,re,glob,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl, MEAL_CATEGORIES
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
have={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
hn={k(x['name']) for x in S if 'gurkerl' in str(x.get('store')).lower()}
CATS=[int(x) for x in sys.argv[1].split(",")] if len(sys.argv)>1 else [134966,135301,135331,135638,135732,136292,137337,137345,137353,137361,137369,137377,137502,137535,137536,137905,137907,137908,137917,137935,137936,137938,137980,137981,137982,138033,138043,138093,135282,135555,135295,137422,137924,137925]
OUT=sys.argv[2] if len(sys.argv)>2 else "/tmp/h05/g_newcats.json"
g=Gurkerl(); seen=set(); out=[]
for c in CATS:
  if c in MEAL_CATEGORIES: continue
  try:
    info=g and __import__('food_connectors.http',fromlist=['get']).get(f'https://www.gurkerl.at/api/v1/categories/normal/{c}')
    ids=[i for i in g.category_ids(c) if i not in seen]
  except Exception as e: print('ERR',c,e); continue
  seen.update(ids); new=[i for i in ids if str(i) not in have]
  ps=[p for p in g.products(new,f"{c} {info.get('name')}") if not p.extra.get('archived') and p.extra.get('in_stock') and k(p.name) not in hn] if new else []
  print(c,info.get('name'),'ids',len(ids),'notin',len(new),'instock-new',len(ps),flush=True)
  out+= [p.__dict__ for p in ps]; time.sleep(0.3)
json.dump(out,open(OUT,'w'),ensure_ascii=False,default=str)
print('TOTAL',len(out))
for p in out: print(p['source_id'],'|',p['category'],'|',p['brand'],'|',p['name'],'|',p['price_eur'],p['size_g'])
