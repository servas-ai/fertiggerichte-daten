# T17: Gurkerl + BILLA ready-meals fetch, keep NEW not-yet-in scored/connectors_new
import json,sys,re,time,collections
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters.rewe import Billa

S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
gid={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
bid={m.group(1) for x in S for m in [re.search(r'(\d{5,})$',str(x.get('url') or ''))] if m and 'billa' in str(x.get('url',''))}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={(k(x['name']),str(x.get('store')).lower()[:4]) for x in S}

BAD=re.compile(r'(sauce|soße|brühe|bouillon|würfel|paste\b|marinade|teig\b|blätterteig|'
  r'faschiertes(?! laib)|gulaschfleisch|suppenfleisch|hummus|aufstrich|gewürz|'
  r'mehl\b|öl\b|baby|hipp|hund|katze|chips|joghurt|eisdessert|smoothie|'
  r'schinken geschn|aufschnitt|salami|würstchen$|reis$|nudeln$|spaghetti$|penne$|'
  r'filet natur|roh\b|suppengemüse|instant.?cup|5 minuten)',re.I)

g=Gurkerl(); b=Billa()
print('Fetching Gurkerl ready-meals...',flush=True)
gp=g.fetch(category='ready-meals', limit=3000)
print('Gurkerl fetched',len(gp),flush=True)
print('Fetching BILLA ready-meals...',flush=True)
bp=b.fetch(category='ready-meals', limit=2000)
print('BILLA fetched',len(bp),flush=True)

out=[]
for src,ps in (('gurkerl',gp),('billa',bp)):
  for p in ps:
    sid=str(p.source_id)
    if p.source_url in urls: continue
    if src=='gurkerl' and sid in gid: continue
    if src=='billa' and sid.lstrip('0') in {x.lstrip('0') for x in bid}: continue
    if (k(p.name),src[:4]) in names: continue
    if BAD.search(p.name or ''): continue
    # skip archived / clearly not meal size extremes later
    out.append(dict(p.__dict__,_src=src))

print('NEW candidates',len(out),collections.Counter(p['_src'] for p in out))
# Prefer those with some meal-ish signal in name/category
MEALISH=re.compile(r'fertig|menü|suppe|eintop|pizza|baguette|flammkuchen|knödel|strudel|gulasch|curry|lasagne|chili|bowl|auflauf|risotto|paella|schnitzel|nugget|fisch|schlemmer|ravioli|tortell|gnocchi|maultaschen|spätzle|fleckerl|gröstl|frikassee|bolognese|carbonara|kaiserschmarrn|germknödel|palatschinken|piccolini|steinofen|dean|youcook|iglo|frosta|wagner|planted|leberknödel|kaspress|faschierte|cordon|gyoza|frühlings|nasi|bami|pad|teriyaki|tikka|minestrone|ragout|geschnetzelt',re.I)
pref=[p for p in out if MEALISH.search(p.get('name') or '') or MEALISH.search(p.get('category') or '')]
print('mealish',len(pref))
json.dump(pref,open('/tmp/h17/ready_new.json','w'),ensure_ascii=False,default=str)
for p in pref[:120]:
  print(p['_src'],p['source_id'],'|',str(p.get('category') or '')[:40],'|',(p.get('brand') or '')[:16],'|',p['name'][:55],'|',p.get('price_eur'),p.get('size_g'))
print('... total mealish',len(pref))
