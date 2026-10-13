# hourly T20 (2026-10-13T20): Gurkerl walk of additional ready-meal-adjacent categories not in MEAL_CATEGORIES
# (TK Baguettes & Flammkuchen 621, TK Rösti/Laibchen/Taschen 136119, TK Geflügel 617, M&S Tiefgekühlt 134312,
#  Kühlregal Knödel/Spätzle 136419, Frische Pasta & Gnocchi 136418); only ids not yet in scored/connectors_new; in-stock only
import json,sys,re
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
g=Gurkerl()
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',re.sub(r'\(tiefgekühlt\)|\(gefroren\)','',(s or '').lower()))
ids_have=set()
for x in S:
  for u in (x.get('url'),x.get('source_url')):
    m=re.search(r'gurkerl\.at/(\d+)-',u or '')
    if m: ids_have.add(int(m.group(1)))
names={k(x['name']) for x in S if 'gurkerl' in str(x.get('store','')).lower()}
CATS={621:'Tiefkühlprodukte > Pizza, Baguettes & Flammkuchen > Baguettes & Flammkuchen',136119:'Tiefkühlprodukte > Kartoffelprodukte > Rösti, Laibchen & Taschen',
      617:'Tiefkühlprodukte > Fleisch > Geflügel',134312:'Marks & Spencer > Tiefgekühlte Produkte',136419:'Kühlregal > Schnelle Küche > Frische Pasta, Spätzle & Knödel > Knödel, Spätzle & Co',
      136418:'Kühlregal > Schnelle Küche > Frische Pasta, Spätzle & Knödel > Frische Pasta & Gnocchi'}
cand={}
for cid,label in CATS.items():
  ids=g.category_ids(cid); n=0
  for i in ids:
    if i in ids_have or i in cand: continue
    cand[i]=label; n+=1
  print(cid,label,len(ids),'new',n,flush=True)
out=[]
for p in g.products(list(cand),None):
  p.category=cand.get(int(p.source_id))
  if p.extra.get('archived') or not p.extra.get('in_stock') or k(p.name) in names: continue
  out.append(p.__dict__)
json.dump(out,open('/tmp/h20/g2_new.json','w'),ensure_ascii=False,default=str,indent=0)
print('total',len(out))
for p in out: print(p['source_id'],'|',p['category'].split(' > ')[-1][:20],'|',p['name'][:70],'|',p['price_eur'],p['size_g'])
