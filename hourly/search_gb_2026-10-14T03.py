# hourly T03: Gurkerl + BILLA dish-stem search, keep only items in meal-type categories not yet present
import json,sys,re,time,collections
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters.rewe import Billa
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
gid={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
bid={m.group(1) for x in S for m in [re.search(r'(\d{5,})$',str(x.get('url') or ''))] if m and 'billa' in str(x.get('url'))}
names={(k(x['name']),str(x.get('store')).lower()[:4]) for x in S}
Q=sys.argv[1].split(',')
MEALCAT=re.compile(r'fertig|menü|schnelle küche|suppe|eintop|pizza|baguette|flammkuchen|paniert|nugget|schnitzel|mehlspeis|knödel|strudel|auflauf|lasagne|asia|curry|bowl|snack.*warm|burger|wrap|dosengericht|konserv.*gericht|gericht',re.I)
NOT=re.compile(r'sauce|soße|fix\b|würz|gewürz|brühe|bouillon|suppenwürfel|teig\b|blätterteig|mehl|hund|katze|chips|aufstrich|dressing|basis|pulver|instant|cup|5 minuten|trocken|beutel|einlage|nudeln$|reis$|marinade|paste',re.I)
g=Gurkerl(); b=Billa(); out=[]; cats=collections.Counter()
for q in Q:
  for src,fn in (('gurkerl',g.search),('billa',b.search)):
    try: ps=fn(q,80)
    except Exception as e: print('ERR',src,q,e,flush=True); continue
    for p in ps:
      sid=str(p.source_id).split('-')[-1]
      if p.source_url in urls or (src=='gurkerl' and sid in gid) or (src=='billa' and sid.lstrip('0') in {x.lstrip('0') for x in bid}): continue
      if (k(p.name),src[:4]) in names: continue
      c=p.category or ''
      if not MEALCAT.search(c+' '+p.name) or NOT.search(p.name): continue
      names.add((k(p.name),src[:4])); urls.add(p.source_url); out.append(dict(p.__dict__,_src=src)); cats[(src,c)]+=1
    time.sleep(0.3)
  print(q,len(out),flush=True)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False,default=str)
for (s,c),n in cats.most_common(40): print(' CAT',s,n,c)
for p in out: print(p['_src'],p['source_id'],'|',str(p['category'])[:45],'|',p['brand'],'|',p['name'],'|',p['price_eur'],p['size_g'])
