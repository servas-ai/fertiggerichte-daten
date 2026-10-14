import json,sys,re,time
sys.path.insert(0,'/workspace/food-connectors')
from food_connectors.adapters.rewe import Billa
from food_connectors.http import get
S=json.load(open('/workspace/fertig/scored.json'))+json.load(open('/workspace/fertig/connectors_new.json'))
urls={x.get('url') for x in S}
k=lambda s:re.sub(r'[^a-z0-9]','',(s or '').lower())
names={k(x['name']) for x in S if 'billa' in str(x.get('store') or '').lower()}
b=Billa()
Q=['dean & david bowl','dean & david teriyaki','dean & david protein','sous vide pulled','pulled duck','pulled pork sous','pulled chicken sous',
   'back mozzarella sticks','planted steak','planted kebab','planted chicken','planted gyros',
   'iglo pizza baguette','iglo baguette','wagner pizza baguette','dr oetker baguette',
   'clever mozzarella sticks','clever meatballs','clever laibchen','clever cevapcici',
   'hofstädter cevapcici','hofstädter fleischlaibchen','hofstädter chicken nuggets',
   'ja natürlich sous vide','ja natürlich gulasch','ja natürlich chili',
   'billa immer gut gulasch','billa immer gut chili','billa corso bowl',
   'omisschmankerl gulasch','omi schmankerl','hink gulasch','hink beuschel',
   'leibspeis gulasch','leitgebs','stadtküche','youcook bowl','youcook curry',
   'frosta vegan bowl','frosta geschnetzeltes','iglo green cuisine bowl',
   'vivera schnitzel','vivera balls','vegetarian butcher','like meat balls',
   'garden gourmet nuggets','rügenwalder vegetarian','billie green schnitzel',
   'endori schnitzel','good catch fish','heura chunks','beyond mince fertig']
seen=set(p['source_id'] for p in json.load(open('/tmp/h07/billa_cand.json')))
out=[]; cands=[]
for q in Q:
  try: ps=b.search(q,40)
  except Exception as e: print('ERR',q,e,flush=True); continue
  n=0
  for p in ps:
    if p.source_id in seen or p.source_url in urls or k(p.name) in names: continue
    seen.add(p.source_id); cands.append(p); n+=1
  if n: print(q,'new',n,flush=True)
  time.sleep(0.2)
MEAL=re.compile(r'(bowl|menü|sous.?vide|pulled|mozzarella.?stick|planted|baguette|pizza|gulasch|chili|curry|schnitzel|nugget|laibchen|cevap|meatball|bällchen|ball|chunk|kebab|gyros|geschnetzelt|beuschel|hink|leibspeis|stadtküche|youcook|frosta|iglo|vivera|garden gourmet|rügenwalder|billie|endori|heura|beyond|good catch|fish)',re.I)
BAD=re.compile(r'(gewürz|paste|sauce|soße|teig\b|käse gerieben|pizzateig|mehl|hendlfilet$|hendl filet|faschiertes|roh\b|natur\b|mince(?! )|hackfleisch|aufschnitt|wurst\b|salami\b(?! pizza)|nassfutter|zooroyal|vital-menü)',re.I)
pick=[p for p in cands if not BAD.search(p.name or '') and MEAL.search(p.name or '') and p.size_g and 50<=p.size_g<900]
print('pick',len(pick),flush=True)
for p in pick[:50]:
  try: b.enrich(p); time.sleep(0.35)
  except Exception as e: p.extra=p.extra or {}; p.extra['err']=str(e)
  n=p.nutrition_100g or {}
  print(p.source_id,'|',p.brand,'|',p.name[:55],'|',p.price_eur,p.size_g,'| kcal',n.get('kcal'),'P',n.get('protein'),'|',(p.producer or '')[:35].replace('\n',' '),flush=True)
  out.append(p.__dict__)
# merge with previous
prev=json.load(open('/tmp/h07/billa_cand.json'))
have={p['source_id'] for p in prev}
for p in out:
  if p['source_id'] not in have: prev.append(p); have.add(p['source_id'])
json.dump(prev,open('/tmp/h07/billa_cand.json','w'),ensure_ascii=False,default=str)
print('TOTAL billa_cand',len(prev))
