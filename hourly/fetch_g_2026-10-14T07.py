import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.gurkerl import Gurkerl
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
ids={str(x.get('url','')).rstrip('/').split('/')[-1].split('-')[0] for x in S if 'gurkerl' in str(x.get('url') or '')}
g=Gurkerl()
print('methods',[m for m in dir(g) if not m.startswith('_')])
# search if available
if hasattr(g,'search'):
  Q=['pulled pork','pulled chicken','pulled duck','sous vide','dean david','mozzarella sticks',
     'planted steak','planted kebab','cevapcici','fleischlaibchen','chicken nuggets',
     'pizza baguette','flammkuchen','pinsa','youcook','stadtküche','leibspeis',
     'iglo baguette','wagner baguette','frosta bowl','green cuisine',
     'kaspressknödel','spinatknödel','leberknödel','serviettenknödel',
     'kaiserschmarrn','germknödel','marillenknödel','topfenknödel',
     'palatschinken','buchteln','lavakuchen','ofenkäse',
     'maultaschen','käsespätzle','schinkenfleckerl','eiernockerl',
     'tiroler gröstl','beuschel','szegediner','fiaker gulasch',
     'hink','omisschmankerl','inzersdorfer chili','felix chili']
  out=[]; seen=set()
  for q in Q:
    try: ps=g.search(q,40)
    except Exception as e: print('ERR',q,e,flush=True); continue
    n=0
    for p in ps:
      if p.source_id in seen or p.source_url in urls or p.source_id in ids: continue
      seen.add(p.source_id); out.append(p); n+=1
    if n: print(q,len(ps),'new',n,flush=True)
    time.sleep(0.25)
  print('candidates',len(out),flush=True)
  # enrich those that look like meals
  MEAL=re.compile(r'(pulled|sous.?vide|dean|mozzarella|planted|cevap|laibchen|nugget|baguette|flammkuchen|pinsa|youcook|stadtküche|leibspeis|bowl|knödel|knoedel|kaiserschmarrn|germknödel|marillen|topfenknödel|palatschinken|buchteln|lavakuchen|maultaschen|spätzle|fleckerl|nockerl|gröstl|beuschel|gulasch|chili|curry|pizza|schnitzel|fish|scholle|dorsch)',re.I)
  BAD=re.compile(r'(gewürz|sauce|soße|teig\b|roh\b|natur\b|aufschnitt|wurst\b|salami\b(?! )|käse gerieben|mehl|öl\b)',re.I)
  pick=[p for p in out if MEAL.search(p.name or '') and not BAD.search(p.name or '')]
  print('pick',len(pick),flush=True)
  enr=[]
  for p in pick[:60]:
    try: g.enrich(p); time.sleep(0.3)
    except Exception as e: p.extra=p.extra or {}; p.extra['err']=str(e)
    n=p.nutrition_100g or {}
    print(p.source_id,'|',p.brand,'|',p.name[:55],'|',p.price_eur,p.size_g,'| stock',(p.extra or {}).get('in_stock'),'| kcal',n.get('kcal'),'P',n.get('protein'),'|',p.ean,flush=True)
    enr.append(p.__dict__)
  json.dump(enr,open('/tmp/h07/g_cand.json','w'),ensure_ascii=False,default=str)
  print('GURKERL',len(enr))
else:
  print('no search method')
  # try categories
  print(getattr(g,'MEAL_CATEGORIES',None))
