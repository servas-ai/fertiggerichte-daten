# hourly T04: for SPAR meal hits without a twin in the dataset, search BILLA + Gurkerl live for the identical product (same brand, pack within 3 %, name tokens) and fetch its label nutrition
import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.adapters.gurkerl import Gurkerl
SIDS=sys.argv[1].split(',')
d={x['spar']['source_id']:x['spar'] for x in json.load(open('/tmp/h04/spar_fuzzy.json'))}
def norm(w): return w.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss')
STOP={'mit','und','in','der','die','das','im','stueck','tiefgekuehlt','er','x','msc','pizza','dr','oetker'}
def toks(t,brand):
  t=norm((t or '').lower()); t=re.sub(r'\(.*?\)',' ',t); t=re.sub(r'\d+(?:[.,]\d+)?\s*(g|kg|ml|l|stueck|stk)\b',' ',t)
  bw={norm(x) for x in re.findall(r'[a-zäöüß]+',(brand or '').lower())}
  return {x for x in re.findall(r'[a-z]+',t) if x not in STOP and x not in bw and len(x)>2}
b=Billa(); g=Gurkerl(); out=[]
for sid in SIDS:
  p=d[sid]; T=toks(p['name'],p.get('brand')); q=p['name']
  q=re.sub(r'\d+\s*Stück','',q).strip()
  res=[]
  for src,fn in (('billa',b.search),('gurkerl',g.search)):
    try: hs=fn(q,30)
    except Exception as e: print('ERR',src,q,e); continue
    for h in hs:
      if not h.size_g or abs(h.size_g-p['size_g'])>0.03*p['size_g']: continue
      X=toks(h.name,h.brand)
      if not X: continue
      j=len(T&X)/len(T|X)
      if j<0.5: continue
      try: h=(b if src=='billa' else g).enrich(h)
      except Exception as e: print('ERR enrich',e)
      res.append(dict(h.__dict__,_src=src,_j=round(j,2)))
    time.sleep(0.4)
  out.append(dict(spar=p,hits=res))
  print(sid,'|',p['name'],'|',p['size_g'],p['price_eur'])
  for h in res: print('   ',h['_src'],h['_j'],'|',h['name'],'|',h['size_g'],h['price_eur'],'|',(h.get('nutrition_100g') or {}).get('kcal'),(h.get('nutrition_100g') or {}).get('protein'),'|',h.get('ean'),'|',h['source_url'])
json.dump(out,open('/tmp/h04/twin_search.json','w'),ensure_ascii=False,default=str)
