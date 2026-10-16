import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters.rewe import Billa
from food_connectors.adapters.mpreis_shop import MpreisShop

keep=json.load(open('/tmp/h17/to_enrich.json'))
g,b,m=Gurkerl(),Billa(),MpreisShop()
out=[]
for p0 in keep:
  src=p0['_src']; sid=str(p0['source_id'])
  try:
    if src=='gurkerl':
      ps=g.products([int(sid)])
      p=ps[0] if ps else None
      if p: g.enrich(p); time.sleep(0.35)
    elif src=='billa':
      # fetch by search of name then match id, or product if available
      if hasattr(b,'product'):
        p=b.product(sid)
      else:
        # re-search and find
        hits=b.search(p0['name'].split()[0]+' '+p0['name'].split()[-1],20)
        p=next((x for x in hits if x.source_id==sid),None)
      if p and hasattr(b,'enrich'):
        try: b.enrich(p)
        except Exception: pass
      time.sleep(0.35)
    else:
      url=p0.get('source_url') or ''
      if hasattr(m,'product') and url:
        p=m.product(url)
      else:
        hits=m.search(p0['name'][:40],20)
        p=next((x for x in hits if str(x.source_id)==sid),None)
      if p and hasattr(m,'enrich'):
        try: m.enrich(p)
        except Exception: pass
      time.sleep(0.35)
  except Exception as e:
    print('ERR',src,sid,e,flush=True); continue
  if not p:
    print('NONE',src,sid,p0['name'][:40],flush=True); continue
  n=p.nutrition_100g or {}
  print(src,p.source_id,'|',p.brand,'|',p.name[:50],'|',p.price_eur,p.size_g,'| stock',(p.extra or {}).get('in_stock') or (p.extra or {}).get('availability'),'| kcal',n.get('kcal'),'P',n.get('protein'),'| img',bool(p.image_url),'|',p.ean,flush=True)
  d=p.__dict__; d['_src']=src; out.append(d)
json.dump(out,open('/tmp/h17/enriched.json','w'),ensure_ascii=False,default=str)
print('ENRICHED',len(out))
