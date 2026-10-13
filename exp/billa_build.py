import json,re,sys,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
B=Billa()
ex=json.load(open('../scored.json'))
have=set()
for x in ex:
  u=x.get('url') or ''
  m=re.search(r'(\d{8})$',u)
  if m: have.add(m.group(1))
  have.add(re.sub(r'\W','',x['name'].lower()))
OK=r'Fertiggerichte ungekühlt > (Gerichte|Suppen)|Fertiggerichte gekühlt > (Menüschalen|Suppen|Süßes|Salate & Dressing > Salate)|Fertiggerichte gekühlt$|Tiefkühlgerichte > Tiefkühlgerichte|Pikante & Süße Knödel|Kühlwaren > Desserts > (Desserts|Pudding)|Rein Pflanzlich > (Schnell & Rein Pflanzlich > Fertiggerichte|Kühlregal > Desserts)|Mehlspeisen & Co|Desserts ungekühlt'
d=json.load(open('billa_all.json'));out=[]
for r in d:
  path=' > '.join(x['name'] for x in (r.get('parentCategories') or [[]])[0])
  if not re.search(OK,path): continue
  slugid=re.sub(r'\D','',r['sku'])
  if slugid in have or re.sub(r'\W','',r['name'].lower()) in have: continue
  p=B._p(r); p.category=path
  out.append(p)
print('new',len(out),flush=True)
res=[]
for i,p in enumerate(out):
  B.enrich(p); res.append(p.to_dict()); time.sleep(0.4)
  if i%50==0: print(i,flush=True)
json.dump(res,open('billa_new.json','w'),ensure_ascii=False)
