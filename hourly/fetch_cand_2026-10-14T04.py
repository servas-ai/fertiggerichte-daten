# hourly T04: detail fetch for hand-picked BILLA / Gurkerl / MPreis candidates (nutrition, EAN, producer, storage)
import json,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters import mpreis_shop as M
B=sys.argv[1].split(',') if len(sys.argv)>1 and sys.argv[1] else []
G=sys.argv[2].split(',') if len(sys.argv)>2 and sys.argv[2] else []
MP=sys.argv[3].split(',') if len(sys.argv)>3 and sys.argv[3] else []
out=[]
b=Billa()
for sku in B:
  hits=[p for p in b.search(sku,5) if p.source_id==sku]
  from food_connectors.adapters.base import Product
  p=hits[0] if hits else Product(source='billa',store='BILLA',name='',source_id=sku,extra={})
  p=b.enrich(p); out.append(dict(p.__dict__,_src='billa')); time.sleep(0.5)
g=Gurkerl()
for gid in G:
  try: p=g.product(gid) if hasattr(g,'product') else None
  except Exception as e: print('ERR g',gid,e); p=None
  if p: out.append(dict(p.__dict__,_src='gurkerl'))
for s in MP:
  p=M.product('https://www.mpreis.at/shop/p/'+s)
  if p: out.append(dict(p.__dict__,_src='mpreis'))
for p in out:
  n=p.get('nutrition_100g') or {}
  print(p['_src'],p['source_id'],'|',p.get('brand'),'|',p.get('name'),'|',p.get('price_eur'),p.get('size_g'),'|',n,'|',p.get('ean'),'|',str(p.get('producer'))[:60],'|',p.get('producer_id'),'|',(p.get('extra') or {}).get('storage'),(p.get('extra') or {}).get('availability'))
json.dump(out,open(sys.argv[4] if len(sys.argv)>4 else '/tmp/h04/cand.json','w'),ensure_ascii=False,default=str,indent=0)
