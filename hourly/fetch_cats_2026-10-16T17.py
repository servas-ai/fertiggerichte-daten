# T17: walk BILLA meal categories + Gurkerl MEAL_CATEGORIES for new in-stock heat-up meals
import json,sys,re,time,collections
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.adapters.gurkerl import Gurkerl, MEAL_CATEGORIES

S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
gid={m.group(1) for x in S for m in [re.search(r'gurkerl\.at/(\d+)-',str(x.get('url') or ''))] if m}
bid={m.group(1) for x in S for m in [re.search(r'(\d{5,})$',str(x.get('url') or ''))] if m and 'billa' in str(x.get('url',''))}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={(k(x['name']),str(x.get('store')).lower()[:4]) for x in S}

MEAL=re.compile(r'(lasagne|gulasch|curry|eintopf|suppe|auflauf|risotto|chili|paella|moussaka|cannelloni|bolognese|carbonara|menü|bowl|baguette|flammkuchen|pizza|knödel|kaiserschmarrn|germknödel|strudel|palatschinken|maultaschen|käsespätzle|fleckerl|gröstl|ragout|frikassee|geschnetzelt|tikka|butter.?chicken|minestrone|ratatouille|gyoza|frühlings|nasi|bami|pad.?thai|faschierte.?s?.?laibchen|cordon|schnitzel|nugget|schlemmer|ofen.?fisch|ravioli|tortellini|tortelloni|gnocchi|piccolini|steinofen|ristorante|youcook|stadtküche|leibspeis|dean.?david|followfood|little.?lunch|erasco|sonnen|inzersdorfer|iglo|frosta|wagner|planted|leberknödel|kaspress|spinatknödel|fish.?stick|fischstäb|brezel.?fisch)',re.I)
BAD=re.compile(r'(sauce|soße|brühe|würfel|paste|marinade|teig\b|roh\b|filet natur|faschiertes(?! laib)|gulaschfleisch|suppenfleisch|hummus|aufstrich|gewürz|mehl|öl\b|baby|hipp|hund|katze|chips|joghurt|eis\b|smoothie|schinken geschn|aufschnitt|salami|würstchen$|reis$|nudeln$|spaghetti$|penne$)',re.I)

b=Billa(); g=Gurkerl()
out=[]; seen=set()

# BILLA categories
print('BILLA cats', b.categories, flush=True)
for cat in b.categories:
  try:
    ps=b.listing(cat=cat, pages=5)
  except Exception as e:
    print('B-ERR',cat,e,flush=True); continue
  nnew=0
  for p in ps:
    sid=str(p.source_id)
    if sid in seen or p.source_url in urls or sid.lstrip('0') in {x.lstrip('0') for x in bid}: continue
    if (k(p.name),'bill') in names: continue
    if BAD.search(p.name or ''): continue
    if not (MEAL.search(p.name or '') or MEAL.search(p.category or '')): continue
    seen.add(sid); out.append(dict(p.__dict__,_src='billa')); nnew+=1
  print('Billa cat',cat,'got',len(ps),'new',nnew,'tot',len(out),flush=True)
  time.sleep(0.4)

# Gurkerl meal categories
print('Gurkerl MEAL_CATEGORIES', MEAL_CATEGORIES, flush=True)
for cat in MEAL_CATEGORIES:
  try:
    # listing?
    if hasattr(g,'listing'):
      ps=g.listing(cat)
    elif hasattr(g,'category'):
      ps=g.category(cat)
    elif hasattr(g,'products_in_category'):
      ps=g.products_in_category(cat)
    else:
      # search by walking - use categories method
      ps=[]
      for m in ['category_products','cat','browse']:
        if hasattr(g,m):
          ps=getattr(g,m)(cat); break
      if not ps and hasattr(g,'search'):
        continue
  except Exception as e:
    print('G-ERR',cat,e,flush=True); continue
  nnew=0
  for p in (ps or []):
    sid=str(p.source_id)
    if sid in seen or sid in gid or p.source_url in urls: continue
    if (k(p.name),'gurk') in names: continue
    if BAD.search(p.name or ''): continue
    if not (MEAL.search(p.name or '') or MEAL.search(p.category or '')): continue
    seen.add(sid); out.append(dict(p.__dict__,_src='gurkerl')); nnew+=1
  print('Gurkerl cat',cat,'got',len(ps or []),'new',nnew,'tot',len(out),flush=True)
  time.sleep(0.35)

json.dump(out,open('/tmp/h17/cat_cands.json','w'),ensure_ascii=False,default=str)
print('CAT TOTAL',len(out),collections.Counter(p['_src'] for p in out))
for p in out:
  print(p['_src'],p['source_id'],'|',str(p.get('category') or '')[:35],'|',(p.get('brand') or '')[:15],'|',p['name'][:55],'|',p.get('price_eur'),p.get('size_g'))
