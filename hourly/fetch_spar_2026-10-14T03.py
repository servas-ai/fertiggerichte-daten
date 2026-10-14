# hourly T03: SPAR search for heat-up meals not yet in dataset; later twin-nutrition
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.spar_shop import SparShop
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
names={k(x['name']) for x in S if 'spar' in str(x.get('store') or '').lower()}
have_sid={m.group(1) for x in S for m in [re.search(r'interspar\.at/p/(\d+)',str(x.get('url') or ''))] if m}
Q=sys.argv[1].split(',')
sp=SparShop(); out=[]; seen=set()
for q in Q:
    try: ps=sp.search(q,80)
    except Exception as e: print('ERR',q,e,flush=True); time.sleep(1); continue
    n=0
    for p in ps:
        sid=str(p.source_id)
        if sid in seen or sid in have_sid or p.source_url in urls or k(p.name) in names: continue
        seen.add(sid); out.append(p); n+=1
    print(q,len(ps),'new',n,flush=True); time.sleep(0.25)
json.dump([p.__dict__ for p in out],open('/tmp/h03/spar_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('TOTAL',len(out))
for p in out[:400]:
  print(p.source_id,'|',p.brand,'|',p.name,'|',p.price_eur,p.size_g,'|',(p.extra or {}).get('stock_status'),'|',p.category)
if len(out)>80: print('... +',len(out)-80)
