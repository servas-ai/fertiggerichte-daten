import json,sys,re,time,collections
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.spar_shop import SparShop
from food_connectors.adapters.alfies import Alfies

S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={(k(x['name']),str(x.get('store')).lower()[:4]) for x in S}

MEAL=re.compile(r'(lasagne|gulasch|curry|eintopf|suppe|auflauf|risotto|chili con|paella|moussaka|cannelloni|bolognese|menü|bowl|baguette|flammkuchen|pizza|knödel|kaiserschmarrn|germknödel|strudel|maultaschen|käsespätzle|fleckerl|gröstl|frikassee|tikka|butter.?chicken|minestrone|gyoza|frühlings|nasi|pad.?thai|faschierte|cordon|schnitzel|nugget|schlemmer|ravioli|tortell|piccolini|steinofen|iglo|frosta|wagner|leberknödel|kaspress)',re.I)
BAD=re.compile(r'(sauce|soße|brühe|würfel|paste|teig\b|hummus|aufstrich|gewürz|mehl|öl\b|baby|chips|filet natur|faschiertes(?! laib)|gulaschfleisch)',re.I)

Q=['rindsgulasch','faschierte laibchen','leberknödel','kaspressknödel','chili con carne',
   'butter chicken','tikka masala','käsespätzle','maultaschen','kaiserschmarrn',
   'wagner steinofen','iglo schlemmerfilet','frosta bowl','piccolinis',
   'dean david','youcook','little lunch','erasco gulasch','inzersdorfer gulasch']

out=[]; seen=set()
sp=SparShop(); al=Alfies()
print('SPAR methods',[m for m in dir(sp) if not m.startswith('_')],flush=True)
print('Alfies methods',[m for m in dir(al) if not m.startswith('_')],flush=True)

for label,fn in (('spar',sp.search),('alfies',al.search)):
  for q in Q:
    try: ps=fn(q,40)
    except Exception as e:
      print('ERR',label,q,e,flush=True); time.sleep(0.4); continue
    n=0
    for p in ps:
      sid=str(p.source_id)
      if sid in seen or p.source_url in urls: continue
      if (k(p.name),label[:4]) in names: continue
      if BAD.search(p.name or ''): continue
      if not (MEAL.search(p.name or '') or MEAL.search(p.category or '')): continue
      seen.add(sid); out.append(dict(p.__dict__,_src=label)); n+=1
    if n: print(label,q,'+',n,'tot',len(out),flush=True)
    time.sleep(0.25)

json.dump(out,open('/tmp/h17/spar_alfies.json','w'),ensure_ascii=False,default=str)
print('TOTAL',len(out),collections.Counter(p['_src'] for p in out))
for p in out:
  print(p['_src'],p['source_id'],'|',str(p.get('category') or '')[:35],'|',(p.get('brand') or '')[:15],'|',p['name'][:55],'|',p.get('price_eur'),p.get('size_g'))
