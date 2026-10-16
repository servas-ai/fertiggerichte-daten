import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters.rewe import Billa
from food_connectors.adapters.mpreis_shop import MpreisShop
from food_connectors.adapters.off import OpenFoodFacts

keep=json.load(open('/tmp/h17/to_enrich2.json'))
# also re-try mpreis items missing nut from enriched
prev=json.load(open('/tmp/h17/enriched.json'))
g,b,m=Gurkerl(),Billa(),MpreisShop()
off=OpenFoodFacts()
out=list(prev)

# Fix Dean&David size via Billa enrich again + dump extra
for p0 in prev:
  if p0.get('_src')=='billa' and 'Dean' in (p0.get('name') or ''):
    print('DD raw', p0.get('name'), p0.get('size_g'), p0.get('extra'), flush=True)

for p0 in keep:
  src=p0['_src']; sid=str(p0['source_id'])
  try:
    if src=='gurkerl':
      ps=g.products([int(sid)])
      p=ps[0] if ps else None
      if p: g.enrich(p); time.sleep(0.3)
    elif src=='billa':
      hits=b.search(p0['name'][:30],30)
      p=next((x for x in hits if x.source_id==sid),None)
      if p: 
        try: b.enrich(p)
        except: pass
      time.sleep(0.3)
    else:
      url=p0.get('source_url') or ''
      p=m.product(url) if url else None
      time.sleep(0.3)
  except Exception as e:
    print('ERR',src,sid,e,flush=True); continue
  if not p: print('NONE',src,sid); continue
  n=p.nutrition_100g or {}
  # OFF fill if missing
  if (not n.get('kcal') or n.get('protein') is None) and p.ean:
    try:
      op=off.product(str(p.ean)) if hasattr(off,'product') else None
      if op is None and hasattr(off,'by_barcode'): op=off.by_barcode(str(p.ean))
      if op is None and hasattr(off,'fetch'): op=off.fetch(str(p.ean))
      if op:
        on=getattr(op,'nutrition_100g',None) or {}
        if on.get('kcal'):
          p.nutrition_100g={**(p.nutrition_100g or {}),**{k:v for k,v in on.items() if v is not None}}
          n=p.nutrition_100g
          print('OFF-fill',p.ean,n.get('kcal'),n.get('protein'),flush=True)
    except Exception as e:
      print('OFF-err',p.ean,e,flush=True)
  print(src,p.source_id,'|',p.brand,'|',p.name[:50],'|',p.price_eur,p.size_g,'| stock',(p.extra or {}).get('in_stock') or (p.extra or {}).get('availability'),'| kcal',n.get('kcal'),'P',n.get('protein'),'| img',bool(p.image_url),'| ean',p.ean,'| prod',(p.producer or '')[:40].replace('\n',' '),flush=True)
  d=p.__dict__; d['_src']=src; out.append(d)

# Also OFF-fill for previously enriched missing nut / try images from OFF
for p in out:
  n=p.get('nutrition_100g') or {}
  if (not n.get('kcal') or n.get('protein') is None) and p.get('ean'):
    try:
      op=None
      for meth in ('product','by_barcode','fetch','get'):
        if hasattr(off,meth):
          try: op=getattr(off,meth)(str(p['ean'])); break
          except: pass
      if op:
        on=getattr(op,'nutrition_100g',None) or {}
        if on.get('kcal'):
          p['nutrition_100g']={**n,**{k:v for k,v in on.items() if v is not None}}
          if not p.get('image_url') and getattr(op,'image_url',None):
            p['image_url']=op.image_url
          print('OFF-backfill',p.get('name','')[:40],p['nutrition_100g'].get('kcal'),flush=True)
    except Exception as e:
      print('OFF-back',e)
  time.sleep(0.2)

json.dump(out,open('/tmp/h17/enriched_all.json','w'),ensure_ascii=False,default=str)
print('ALL',len(out))
