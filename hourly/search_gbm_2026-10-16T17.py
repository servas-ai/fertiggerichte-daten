# hourly T17: Gurkerl + BILLA + MPreis dish-stem search for NEW true heat-up meals
import json,sys,re,time,collections,glob
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
from food_connectors.adapters.rewe import Billa
from food_connectors.adapters.mpreis_shop import MpreisShop

S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
urls={x.get('url') for x in S}
gid={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
bid={m.group(1) for x in S for m in [re.search(r'(\d{5,})$',str(x.get('url') or ''))] if m and 'billa' in str(x.get('url',''))}
mid={str(x.get('url','')).rstrip('/').split('/')[-1] for x in S if 'mpreis' in str(x.get('url') or '').lower()}
# also collect from ean/name
names={(k(x['name']),str(x.get('store')).lower()[:4]) for x in S}
insp=set()
for f in glob.glob('/workspace/fertig/hourly/cand_gurkerl*.json')+glob.glob('/workspace/fertig/hourly/cand_mpreis*.json')+glob.glob('/tmp/h*/g_cand.json')+glob.glob('/tmp/h*/billa*.json'):
  try:
    d=json.load(open(f))
    if isinstance(d,dict): d=list(d.values()) if d and isinstance(next(iter(d.values()),None),dict) else [d]
    for p in d:
      if isinstance(p,dict):
        insp.add(str(p.get('source_id') or ''))
  except Exception: pass

MEALCAT=re.compile(r'fertig|menü|schnelle küche|suppe|eintop|pizza|baguette|flammkuchen|paniert|nugget|schnitzel|mehlspeis|knödel|strudel|auflauf|lasagne|asia|curry|bowl|burger|wrap|dosengericht|konserv.*gericht|gericht|gulasch|risotto|chili|paella|moussaka|cannelloni|pastagericht|tiefkühl.*(fleisch|geflügel|fisch|snack|mehlspeis)|feinkost',re.I)
NOT=re.compile(r'sauce|soße|fix\b|würz|gewürz|brühe|bouillon|suppenwürfel|teig\b|blätterteig|mehl\b|hund|katze|chips|aufstrich|dressing|basis|pulver|instant.?cup|5 minuten|trocken|beutel|einlage|marinade|paste\b|würstchen$|salami|aufschnitt|käse gerieben|öl\b|essig|reis$|nudeln$|spaghetti$|penne$|farfalle$',re.I)
# Prefer complete meals
PREF=re.compile(r'lasagne|gulasch|curry|eintopf|suppe|auflauf|risotto|chili|paella|moussaka|cannelloni|bolognese|carbonara|menü|teller|bowl|baguette|flammkuchen|pizza|knödel|kaiserschmarrn|germknödel|strudel|palatschinken|maultaschen|käsespätzle|schinkenfleckerl|gröstl|ragout|frikassee|geschnetzeltes|stroganoff|tikka|butter.?chicken|dal\b|minestrone|ratatouille|enchilada|burrito|gyoza|frühlingsrolle|nasi|bami|pad.?thai|pho\b|ramen|jambalaya|würstelsuppe|erdäpfelsuppe|kürbis|linseneintopf|erbsensuppe|hühnersuppe|rindsuppe|tomatensuppe|kartoffelsuppe|gulaschsuppe|chili.?con|faschierte|laibchen.?mit|schnitzel.?mit|cordon',re.I)

Q=[
  # Austrian classics / complete dishes
  'rindsgulasch','szegediner','fiaker gulasch','tiroler gröstl','käsespätzle','schinkenfleckerl',
  'eiernockerl','krautfleckerl','beuschel','tafelspitz','schweinsbraten','zwiebelrostbraten',
  'faschierte laibchen','leberknödel','kaspressknödel','spinatknödel','serviettenknödel',
  'kaiserschmarrn','germknödel','marillenknödel','topfenknödel','palatschinken','apfelstrudel',
  # Soups / stews
  'gulaschsuppe','erbsensuppe','linseneintopf','kartoffelsuppe','kürbiscremesuppe','tomatencremesuppe',
  'hühnersuppe','rindsuppe','minestrone','broccolicremesuppe','karottensuppe','zwiebelsuppe',
  # International complete
  'butter chicken','tikka masala','chicken korma','massaman','tom kha','pad thai','nasi goreng',
  'bami goreng','paella','moussaka','chili con carne','ratatouille','enchilada','burrito bowl',
  'cannelloni','ravioli gefüllt','tortelloni','lasagne vegetarisch','spinach lasagne',
  # Brands / ready trays
  'youcook','stadtküche','leibspeis','dean david','apetito','bedford','followfood',
  'little lunch','erasco','sonnen bassermann','inzersdorfer','felix gulasch','hink',
  'omis schmankerl','simply good','ja natürlich fertig','billa immer gut menü',
  'spar menü','s-budget gulasch','natur pur fertig',
  # Frozen complete
  'iglo menü','frosta menü','frosta bowl','wagner pizza','ristorante pizza',
  'iglo schlemmerfilet','iglo ofenfisch','green cuisine menü',
  # Fresh pasta filled dishes / heat-up
  'maultaschen','ravioli spinat','tortellini käse','gnocchi auflauf',
  # More
  'pulled pork menü','chicken teriyaki','sweet sour chicken','entenbrust','duck curry',
  'vegan gulasch','vegan curry','planted bowl','garden gourmet menü',
]

g,b,m=Gurkerl(),Billa(),MpreisShop()
out=[]; cats=collections.Counter(); seen=set()

def consider(src,p):
  sid=str(p.source_id)
  if sid in seen: return
  if p.source_url in urls: return
  if src=='gurkerl' and sid in gid: return
  if src=='billa' and sid.lstrip('0') in {x.lstrip('0') for x in bid}: return
  if src=='mpreis' and (sid in mid or str(p.source_url).rstrip('/').split('/')[-1] in mid): return
  if (k(p.name),src[:4]) in names: return
  c=(p.category or '')+' '+(p.name or '')
  if not MEALCAT.search(c): return
  if NOT.search(p.name or ''): return
  if not PREF.search(p.name or '') and not MEALCAT.search(p.category or ''): return
  seen.add(sid); names.add((k(p.name),src[:4])); urls.add(p.source_url)
  out.append(dict(p.__dict__,_src=src)); cats[(src,p.category or '?')]+=1

for q in Q:
  for src,fn in (('gurkerl',g.search),('billa',b.search),('mpreis',m.search)):
    try:
      ps=fn(q,60)
    except Exception as e:
      print('ERR',src,q,e,flush=True); time.sleep(0.5); continue
    before=len(out)
    for p in ps: consider(src,p)
    if len(out)>before: print(q,src,'+',len(out)-before,'tot',len(out),flush=True)
    time.sleep(0.25)

json.dump(out,open('/tmp/h17/cand_search.json','w'),ensure_ascii=False,default=str)
print('TOTAL',len(out),flush=True)
for (s,c),n in cats.most_common(40): print(' CAT',s,n,c)
for p in out: print(p['_src'],p['source_id'],'|',str(p.get('category') or '')[:40],'|',p.get('brand'),'|',p['name'][:60],'|',p.get('price_eur'),p.get('size_g'))
