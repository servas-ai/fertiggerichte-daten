# hourly T04: brand-line searches at Gurkerl/BILLA (items not yet in dataset) incl. label nutrition
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.adapters.gurkerl import Gurkerl
S=json.load(open('scored.json'))+json.load(open('connectors_new.json'))
urls={x.get('url') for x in S}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={k(x['name']) for x in S}
b=Billa(); g=Gurkerl(); out=[]
for src,q in [(s,q) for q in sys.argv[1].split(',') for s in ('gurkerl','billa')]:
  fn=g if src=='gurkerl' else b
  try: hs=fn.search(q,40)
  except Exception as e: print('ERR',e); continue
  for h in hs:
    if h.source_url in urls or k(h.name) in names: continue
    if not re.search(q.split()[0][:5],(h.name+' '+(h.brand or '')),re.I): continue
    try: h=fn.enrich(h)
    except Exception: pass
    urls.add(h.source_url); out.append(dict(h.__dict__,_src=src))
    n=h.nutrition_100g or {}
    print(src,h.source_id,'|',h.brand,'|',h.name,'|',h.price_eur,h.size_g,'|',h.category,'|',n.get('kcal'),n.get('protein'),'|',h.ean,'|',(h.extra or {}).get('in_stock'),(h.extra or {}).get('storage'),flush=True)
  time.sleep(0.4)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,default=str,indent=0)
