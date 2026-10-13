# hourly T20 (2026-10-13T20): dm.at (sitemap slug match + products.dm.de JSON) and Shopify meal-prep shops (PrepMyMeal, LiveFresh, Gourmetfein);
# only products whose URL / dan / name+store are not yet in scored/connectors_new
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters import dm_shop as DM
from food_connectors.adapters import mealprep as MP
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}|{x.get('source_url') for x in S}
dans={m.group(1) for u in urls if u and 'dm.at' in u for m in [re.search(r'/p/d/(\d+)/',u) or re.search(r'-p?(\d{5,})\.html',u)] if m}
names={(k(x['name']),str(x.get('store','')).lower()) for x in S}
out=[]
us=[u for u in DM.sitemap_urls() if DM.SLUG.search(u.rsplit('/',1)[1]) and not DM.SLUG_NOT.search(u.rsplit('/',1)[1])]
new=[u for u in us if u not in urls and re.search(r'/p/d/(\d+)/',u).group(1) not in dans]
print('dm slug urls',len(us),'new',len(new),flush=True)
for u in new:
    dan=int(re.search(r'/p/d/(\d+)/',u).group(1))
    try: p=DM.product(dan,u)
    except Exception as e: print('ERR',u,e); continue
    time.sleep(1.0)
    if not DM.is_ready_meal(p) or (k(p.name),'dm') in names: continue
    out.append(p.__dict__); print('dm',p.name,p.price_eur,p.size_g,flush=True)
for cls in (MP.PrepMyMeal,MP.LiveFresh,MP.Gourmetfein):
    a=cls()
    try: ps=a.fetch(limit=400)
    except Exception as e: print('ERR',cls.__name__,e); continue
    n=0
    for p in ps:
        if p.source_url in urls or (k(p.name),a.store.lower()) in names: continue
        out.append(p.__dict__); n+=1; print(a.id,p.name,p.price_eur,p.size_g,flush=True)
    print(cls.__name__,len(ps),'new',n,flush=True)
json.dump(out,open('/tmp/h20/dm_mp_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
